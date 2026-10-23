# IB Math AA HL Flashcards

Anki flashcards for IB Mathematics: Analysis and Approaches HL, one subdeck per textbook chapter.

## For students

### Download

**[Download the latest deck](https://github.com/alxmjo/ib-math-aa-hl-anki/releases/latest/download/IB_Math_AA_HL.apkg)**

The link always gives the newest version. Bookmark it.

### First import

- **Android (AnkiDroid):** tap the link, then open the downloaded file with AnkiDroid.
- **iPhone or iPad (AnkiMobile):** tap the link in Safari, open the download, tap Share and choose AnkiMobile.
- **Computer (Anki):** download the file, then use File → Import, or double-click the file.

If the import screen offers **Import any deck presets**, turn it on the first time. This sets the deck to 10 new cards per day.

The cards appear under **IB Math AA HL**, with one subdeck per chapter.

### Updating

When a new version is announced, download from the same link and import it the same way. Keep the import options at their defaults. Edited cards update in place and your review progress is kept.

### Removing retired cards

Importing never deletes cards. When a card is retired, the release notes give a search such as `ID:1.4-C35 OR ID:1.4-D01`. In Anki, open Browse, paste the search, select the cards it finds and delete them.

## For maintenance

### Files

- `csv/` holds one file per chapter, with the columns id, section, type, front, back, extra, tags, active.
- `build.sh` holds the build command for every chapter and writes `dist/IB_Math_AA_HL.apkg`.
- `build_math_deck.py` is the builder (genanki).
- `.github/workflows/release.yml` builds the deck and attaches it to each published release.

### Conventions

- Maths uses Anki's MathJax: `\( … \)` inline, `\[ … \]` display.
- Card types: Rule and Strategy. The Why and any worked example go in Extra.
- Subdeck titles are the code plus the chapter name (`IB Math AA HL::1.4 Equations`). The subdeck ID comes from the code alone, so a chapter can be renamed safely.
- Tags: section code (`1.4C`) and `type::rule` or `type::strategy`. Note IDs: `1.4-C03`.
- Preset: 10 new cards per day, siblings buried.

### Never change once students have the deck

- `MODEL_ID` and `PRESET_ID` in `build_math_deck.py`.
- A chapter's `--ref` code in `build.sh`.
- Any card's `id` in a CSV. The note identity comes from the code and the card id, so edited cards update in place on re-import and students keep their progress.

### Releasing

1. Commit and push the CSV changes. This does not change what students download.
2. Test the built deck in Anki.
3. Publish a release (for example tag `v2026-10-23`). The workflow builds the deck and attaches it, and the student download link then serves the new version.
4. Retire a card by setting `active` to `no`; never delete the row. List retired IDs in the release notes as a Browse search, for example `ID:1.4-C35 OR ID:1.4-D01`.
