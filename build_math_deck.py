#!/usr/bin/env python3
r"""IB Math AA HL flashcards: cards CSV -> Anki .apkg (LaTeX rendered by Anki's built-in MathJax).

Usage (normally run through build.sh):
  python3 build_math_deck.py --csv csv/1.4_equations.csv --ref 1.4 --name "Equations" \
      --csv csv/1.5_sequences_series.csv --ref 1.5 --name "Sequences and Series"
Subdeck title: code + chapter name ("IB Math AA HL::1.4 Equations"). The subdeck ID is derived
from the code alone, so renaming a chapter never creates a new deck.
Tags, labels and note IDs use the code only: tag 1.4C, note ID 1.4-C03 (Browse search: ID:1.4-C03).

CSV columns: id, section, type, front, back, extra, tags, active
  type  = Rule | Strategy
  maths = \( ... \) inline, \[ ... \] display;  HTML allowed (<br>, <b>)
"""
import argparse, csv, hashlib, json, os, shutil, sqlite3, zipfile
import genanki

DECK_ROOT = "IB Math AA HL"
NEW_PER_DAY = 10
# ---------------- stable IDs (do not change) ----------------
MODEL_ID = 1760000002101
PRESET_ID = 1760000002301

FIELDS = ["Front", "Back", "Extra", "Type", "Section", "ID"]
FRONT = ('<div class="meta"><span class="badge">{{Type}}</span> <span class="sec">{{Section}}</span></div>'
         '<div class="q">{{Front}}</div>')
BACK = ('{{FrontSide}}<hr id=answer><div class="a">{{Back}}</div>'
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
mjx-container[display="true"]{overflow-x:auto;overflow-y:hidden;max-width:100%}"""


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
    root = genanki.Deck(deck_id(DECK_ROOT), DECK_ROOT)
    decks = [root]
    for path, ref, chapter in zip(a.csv, a.ref, a.name):
        name = f"{DECK_ROOT}::{ref} {chapter}"
        d = genanki.Deck(deck_id(f"{DECK_ROOT}::{ref}"), name)  # ID from the code only
        prefix = ref
        for r in csv.DictReader(open(path, encoding="utf-8")):
            if r.get("active", "yes").strip().lower() == "no":
                continue
            d.add_note(genanki.Note(model=model, guid=genanki.guid_for(prefix, r["id"]),
                fields=[r["front"], r["back"], r["extra"], r["type"],
                        f'{ref}{r["section"]}', f'{prefix}-{r["id"]}'],
                tags=r["tags"].split()))
        decks.append(d)
        print(f"{name}: {len(d.notes)} cards")
    genanki.Package(decks).write_to_file(a.out)
    set_preset(a.out, [d.deck_id for d in decks])
    print("->", a.out)


if __name__ == "__main__":
    main()
