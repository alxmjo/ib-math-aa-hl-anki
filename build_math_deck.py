#!/usr/bin/env python3
r"""IB Math AA HL flashcards: cards CSV -> Anki .apkg (LaTeX rendered by Anki's built-in MathJax).

Usage (normally run through build.sh):
  python3 build_math_deck.py --csv csv/1.4_equations.csv --ref 1.4 --name "Equations" \
      --csv csv/1.5_sequences_series.csv --ref 1.5 --name "Sequences and Series"
Subdeck title: zero-padded code + chapter name ("IB Math AA HL::1.04 Equations"), so Anki lists the
chapters in order. The subdeck ID is derived from the unpadded code alone, so renaming a chapter never
creates a new deck.
Tags, labels and note IDs use the code only: tag 1.4C, note ID 1.4-C03 (Browse search: ID:1.4-C03).

CSV columns: id, section, type, front, back, extra, tags, active
  type  = Rule | Strategy
  maths = \( ... \) inline, \[ ... \] display;  HTML allowed (<br>, <b>)
Cloze cards: put the text with {{c1::...}} in the front column and leave back empty.
  They use the "IB Math cloze" note type. Keep each cloze marker outside the maths delimiters.
Words attached to a short maths expression (\(x\)-axis, \(n\)th) are kept on one line automatically.
Figures: write [fig:NAME] in any field; the builder inlines figures/NAME.svg (see figures/make_figures.py).
Quotes: quotes.csv (code, quote, author, source) gives each chapter subdeck one quote card, with the quote
  on the front and the attribution on the back (Type "Quote", card ID 1.4-Q01, tag type::quote).
  It is added first, so it is the first new card in its chapter. A chapter without a row gets no quote card.
"""
import argparse, csv, hashlib, json, os, re, shutil, sqlite3, zipfile
import genanki

DECK_ROOT = "IB Math AA HL"
NEW_PER_DAY = 10
# ---------------- stable IDs (do not change) ----------------
MODEL_ID = 1760000002101
CLOZE_MODEL_ID = 1760000002102
PRESET_ID = 1760000002301

FIELDS = ["Front", "Back", "Extra", "Type", "Section", "ID"]
FRONT = ('<div class="meta"><span class="badge">{{Type}}</span> <span class="sec">{{Section}}</span></div>'
         '<div class="q">{{Front}}</div>')
BACK = ('{{FrontSide}}<hr id=answer><div class="a">{{Back}}</div>'
        '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}')
CLOZE_FIELDS = ["Text", "Extra", "Type", "Section", "ID"]
CLOZE_FRONT = ('<div class="meta"><span class="badge">{{Type}}</span> <span class="sec">{{Section}}</span></div>'
               '<div class="q">{{cloze:Text}}</div>')
CLOZE_BACK = ('<div class="meta"><span class="badge">{{Type}}</span> <span class="sec">{{Section}}</span></div>'
              '<div class="q">{{cloze:Text}}</div>'
              '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}')
CSS = """.card{font-family:system-ui,-apple-system,sans-serif;font-size:20px;line-height:1.5;
text-align:center;color:#222;background:#fff;padding:0 8px}
.card.nightMode{color:#eee;background:#1e1e1e}
.meta{font-size:12px;color:#888;margin-bottom:10px}
.badge{border:1px solid #888;border-radius:10px;padding:1px 8px}
.q{font-size:21px}.a{font-size:21px}
.extra{font-size:15px;color:#666;margin-top:14px;padding-top:8px;border-top:1px dashed #ccc}
.nightMode .extra{color:#aaa}
.extra{text-align:left;display:inline-block;max-width:100%}
mjx-container[display="true"]{overflow-x:auto;overflow-y:hidden;max-width:100%}
.cloze{font-weight:bold;color:#1a5fb4}
.nightMode .cloze{color:#8ab4f8}
.fig{margin:10px auto 4px;text-align:center}
.fig svg{width:240px;max-width:100%;height:auto}
.nightMode .fig .acc{stroke:#8ab4f8}
.nightMode .fig .acct{fill:#8ab4f8}"""


FIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
QUOTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quotes.csv")


QUOTE_ID = "Q01"  # one quote card per chapter; never change once published


def load_quotes():
    """(front, back) of each chapter's quote card, keyed by chapter code, from quotes.csv."""
    if not os.path.exists(QUOTES):
        return {}
    out = {}
    for r in csv.DictReader(open(QUOTES, encoding="utf-8")):
        credit = r["author"] + (f", {r['source']}" if r["source"].strip() else "")
        out[r["code"].strip()] = (f"“{r['quote'].strip()}”", f"— {credit}")
    return out


def with_figures(text, card_id):
    def inline(m):
        path = os.path.join(FIG_DIR, m.group(1) + ".svg")
        if not os.path.exists(path):
            raise SystemExit(f"{card_id}: figure {m.group(1)} not found in figures/")
        return '<div class="fig">' + open(path, encoding="utf-8").read().strip() + "</div>"
    return re.sub(r"\[fig:([\w.\-]+)\]", inline, text)


def title_code(ref):
    """Chapter code as shown in the subdeck title, zero-padded so Anki lists chapters in order (1.4 -> 1.04).
    Only the title is padded; the deck ID, tags, labels and card IDs use the unpadded code."""
    book, chapter = ref.split(".")
    return f"{book}.{int(chapter):02d}"


NOWRAP = re.compile(r"\\\([^\\]{1,12}\\\)-?[A-Za-z]+")


def keep_together(text):
    """Stop a line break between a short maths expression and the word attached to it,
    as in \\(x\\)-axis or \\(n\\)th: the browser may otherwise break after the maths."""
    return NOWRAP.sub(lambda m: f'<span style="white-space:nowrap">{m.group(0)}</span>', text)


def deck_id(name):
    return int(hashlib.sha1(name.encode()).hexdigest()[:12], 16) % (1 << 31) + 1_000_000_000


def set_preset(apkg, ids):
    tmp = apkg + "_x"; shutil.rmtree(tmp, ignore_errors=True)
    with zipfile.ZipFile(apkg) as z: z.extractall(tmp)
    db = sqlite3.connect(os.path.join(tmp, "collection.anki2"))
    dconf, decks = map(json.loads, db.execute("select dconf, decks from col").fetchone())
    c = json.loads(json.dumps(dconf["1"]))
    c.update(id=PRESET_ID, name=f"{DECK_ROOT} preset", buryInterdayLearning=True)
    c["new"]["bury"] = c["rev"]["bury"] = True
    c["new"]["perDay"] = NEW_PER_DAY
    dconf[str(PRESET_ID)] = c
    for i in ids: decks[str(i)]["conf"] = PRESET_ID
    db.execute("update col set dconf=?, decks=?", (json.dumps(dconf), json.dumps(decks)))
    db.commit(); db.close(); os.remove(apkg)
    with zipfile.ZipFile(apkg, "w", zipfile.ZIP_DEFLATED) as z:
        for f in os.listdir(tmp): z.write(os.path.join(tmp, f), f)
    shutil.rmtree(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", action="append", required=True)
    ap.add_argument("--ref", action="append", required=True, help='book.chapter, e.g. 1.4 -> tags/labels 1.4A, 1.4B ...')
    ap.add_argument("--name", action="append", required=True, help='chapter name, e.g. "Equations"')
    ap.add_argument("--out", default="IB_Math_AA_HL.apkg")
    a = ap.parse_args()
    if not len(a.csv) == len(a.ref) == len(a.name):
        ap.error("give one --csv, --ref and --name for each chapter")
    model = genanki.Model(MODEL_ID, "IB Math card", fields=[{"name": f} for f in FIELDS],
                          templates=[{"name": "Card", "qfmt": FRONT, "afmt": BACK}],
                          css=CSS, sort_field_index=5)
    cloze_model = genanki.Model(CLOZE_MODEL_ID, "IB Math cloze", fields=[{"name": f} for f in CLOZE_FIELDS],
                                templates=[{"name": "Cloze", "qfmt": CLOZE_FRONT, "afmt": CLOZE_BACK}],
                                css=CSS, sort_field_index=4, model_type=genanki.Model.CLOZE)
    root = genanki.Deck(deck_id(DECK_ROOT), DECK_ROOT)
    decks = [root]
    quotes = load_quotes()
    for path, ref, chapter in zip(a.csv, a.ref, a.name):
        name = f"{DECK_ROOT}::{title_code(ref)} {chapter}"
        d = genanki.Deck(deck_id(f"{DECK_ROOT}::{ref}"), name)  # ID from the code only
        prefix = ref
        if ref in quotes:  # added first so it is the chapter's first new card
            front, back = quotes[ref]
            d.add_note(genanki.Note(model=model, guid=genanki.guid_for(prefix, QUOTE_ID),
                tags=[ref, "type::quote"], fields=[front, back, "", "Quote", ref, f"{prefix}-{QUOTE_ID}"]))
        for r in csv.DictReader(open(path, encoding="utf-8")):
            if r.get("active", "yes").strip().lower() == "no":
                continue
            guid = genanki.guid_for(prefix, r["id"])
            label, card_id = f'{ref}{r["section"]}', f'{prefix}-{r["id"]}'
            for fld in ("front", "back", "extra"):
                r[fld] = with_figures(keep_together(r[fld]), card_id)
            if "{{c1::" in r["front"]:
                if r["back"].strip():
                    raise SystemExit(f"{card_id}: a cloze card must leave the back column empty")
                d.add_note(genanki.Note(model=cloze_model, guid=guid, tags=r["tags"].split(),
                    fields=[r["front"], r["extra"], r["type"], label, card_id]))
            else:
                d.add_note(genanki.Note(model=model, guid=guid, tags=r["tags"].split(),
                    fields=[r["front"], r["back"], r["extra"], r["type"], label, card_id]))
        decks.append(d)
        print(f"{name}: {len(d.notes)} cards")
    genanki.Package(decks).write_to_file(a.out)
    set_preset(a.out, [d.deck_id for d in decks])
    print("->", a.out)


if __name__ == "__main__":
    main()
