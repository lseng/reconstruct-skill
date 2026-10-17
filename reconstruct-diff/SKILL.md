---
name: reconstruct-diff
description: >-
  Scores the rebuild against the original: weighted feature parity with an
  evidence report, a screenshot layout diff that ignores colour, and in mode B
  a REA behavioural comparison of the same scenario on both apps. Ends in a
  shippable / not shippable verdict. Use when the user says "how close is it",
  "compare to the original", "what's missing", "parity check", "diff the
  screens", "is it ready", or after /reconstruct-test.
---

# reconstruct-diff

Two standard-library Python tools in this folder, plus REA in mode B:

```bash
python3 parity.py reconstruct/features.csv --require-evidence
python3 imgdiff.py reconstruct/screens/S07.png reconstruct/clone-screens/S07.png --out reconstruct/diffs/S07.png
python3 imgdiff.py a.png b.png --json > reconstruct/diffs/S07.json
python3 parity.py reconstruct/features.csv --visual reconstruct/diffs/*.json --markdown > reconstruct/parity.md
```

## What parity means here

The rebuild does the same job. It does not have to look the same. The feature
score is the number that matters. The layout score checks structure and
ignores colour. A score is only as good as the matrix, so the evidence report
comes with it.

Clean room holds here too. Close a gap by building the behaviour, not by
copying the original's markup, assets or captured responses to push a score
up. Do not chase pixel parity with a third party's app: its exact look is its
trade dress.

## Step 1: feature parity

Every row's `clone` is `yes`, `partial` (with a note), `no`, or `skip` (with a
reason). Then:

```bash
python3 parity.py reconstruct/features.csv --require-evidence
```

Weights must 3, should 2, could 1. Partial counts half. `skip` and your own
additions are not scored. It prints the score, must-haves done of total,
areas weakest first, the missing list in build order, and the evidence split
(artifact / public / none), with must-haves that are still a guess.
`--require-evidence` exits 1 while any counted row has no evidence.

## Step 2: layout diff

Same viewport (1440x900, 390x844), same state, both sides. Originals in
`reconstruct/screens/`, the rebuild in `reconstruct/clone-screens/`.

```bash
python3 imgdiff.py reconstruct/screens/S07.png reconstruct/clone-screens/S07.png --out reconstruct/diffs/S07.png
```

Layout mode compares edge maps on a grid (matches 90+, close 75+, partly 50+)
and lists differing regions in the original's coordinates. `--mode pixel` is
for your own regressions only. For exact pixel metrics with self-verifying
inputs, REA's `compare_web_screenshots` does the same job.

## Step 3: behaviour diff

Mode A: walk each flow in both apps by hand. Mode B: run the same declared
scenario on the rebuild that `/reconstruct-test` captured on the original,
then compare with `compare_web_captures` or `compare_process_captures`. Feed
the comparison Evidence IDs into `verify_reconstruction` as behavioural
claims, one per must-have flow. Pass means every declared claim has complete
comparable evidence. Unknown stays unknown and is never rounded up to pass.

For a full obligation ledger on a large or high-stakes rebuild,
`build_reconstruction_obligation_ledger` and `evaluate_reconstruction_coverage`
are available through `reverse-engineer-anything`. They need a reviewed
Evidence bundle, so use them when the rigor is worth the setup.

Write each difference as: flow, original does, rebuild does, fix or keep.
Fewer clicks than the original is a win.

## Step 4: the report

`reconstruct/parity.md`: overall, feature and layout scores, evidence split,
missing features in build order, behaviour differences (with REA verdicts in
mode B), and a verdict:

- **not shippable**: any must-have missing, any open S1, or a must-have whose
  behaviour claim failed
- **shippable**: all must-haves done, feature score 80+, no open S1 or S2, the
  sweep clean, and no must-have resting on a guess
- **better than the original**: shippable, plus deliberate improvements

Honest numbers. A rebuild at 62% is at 62%.

## Output

`parity.md`, diff images, and the top five things to build next. Then
`/reconstruct-sweep` before anything ships, or `/reconstruct-build` for gaps.
