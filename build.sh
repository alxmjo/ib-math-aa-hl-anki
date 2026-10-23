#!/usr/bin/env bash
# Builds every chapter into dist/IB_Math_AA_HL.apkg.
# To add a chapter: put its CSV in csv/ and add one --csv/--ref/--name line below.
# Never change a chapter's --ref once students have the deck (the subdeck ID comes from it).
set -euo pipefail
mkdir -p dist

python3 build_math_deck.py --out dist/IB_Math_AA_HL.apkg \
  --csv csv/1.4_equations.csv          --ref 1.4 --name "Equations" \
  --csv csv/1.5_sequences_series.csv   --ref 1.5 --name "Sequences and Series"
