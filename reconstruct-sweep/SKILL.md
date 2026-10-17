---
name: reconstruct-sweep
description: >-
  The ship gate for a rebuild: finds anything of the original left in the
  codebase (its name, domains and brand colours, including inside identifiers)
  and, in mode B, distinctive identifiers and strings from the REA evidence
  that would mean decompiled or bundle code leaked into the rebuild. Exits 1
  until clean. Use when the user says "check for leftovers", "is it clean",
  "clean-room check", "sweep", or before anything ships.
---

# reconstruct-sweep

```bash
python3 sweep.py . --avoid "Original Name,Its Company" --domains original.com --colors "#006bff"
python3 sweep.py . --config reconstruct/sweep.json
```

`reconstruct/sweep.json` holds `avoid`, `domains` and `colors`. The sweep
searches file contents and names, including inside identifiers (`OriginalEmbed`),
and skips `node_modules`, build output and the `reconstruct/` planning folder,
where the original's name belongs. Exit 1 means something is left.

## Step 1: identity

`avoid`: the original's product and company names. `domains`: its domains
and CDN hosts. `colors`: its brand colours (if the rebuild is rebranding). If
the target is our own product and keeping its name is the point, say so in
`scope.md` and leave those out.

## Step 2: clean-room markers (mode B)

Decompiled or bundle code leaking in is the failure mode tier B adds. From the
REA evidence, pick 10 to 30 identifiers that a fresh implementation would not
reproduce by accident:

- internal class, module and function names (`FooBookingCoordinatorV2`)
- distinctive string constants, error messages, analytics event names
- private endpoint paths and header names

Add them to `avoid` (or `domains` for hosts). Common words do not belong here
because they only make noise. A hit is a question to answer, not automatically
a leak: rename it if it came from the evidence, keep it and note why if it is
a standard term.

Also check by hand: no files exported from REA sessions (evidence bundles,
pseudocode dumps, extracted assets) anywhere outside `reconstruct/`, and none
committed.

## Step 3: run until clean

```bash
python3 sweep.py . --config reconstruct/sweep.json
```

Fix until it says clean. Then check by eye: favicon, page titles, email
templates, OG image, app icon.

## Output

`reconstruct/sweep.json`, a clean sweep (exit 0), and one line in
`reconstruct/parity.md` recording the date it passed. A rebuild does not ship
until this is clean.
