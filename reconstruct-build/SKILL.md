---
name: reconstruct-build
description: >-
  Builds the rebuild: measures the design system into tokens with a WCAG
  contrast check, builds the primitives, then the core flow as a vertical
  slice, then every screen with all its states, ticking off the feature
  matrix. Every line written fresh, clean-room. Use when the user says "build
  the rebuild", "build screen S07", "match the design", "design tokens",
  "start building", or after /reconstruct-architect.
---

# reconstruct-build

Reads `reconstruct/recon.md`, `architecture.md`, `screens/`. Writes
`reconstruct/design/` (`tokens.json` from the template here, `components.md`),
the app code, `reconstruct/build-log.md`, and updates the `clone` column of
`features.csv`.

```bash
python3 "${CLAUDE_SKILL_DIR}/contrast.py" reconstruct/design/tokens.json     # every text pair, WCAG ratio
```

Read `reconstruct/scope.md` first. REA is used only if it records mode B with
a ticked basis. If it is missing or has no basis, work in mode A and say so.

## The rules

- **Clean room.** This stage is the clean room. Code is written from
  `recon.md`, `architecture.md` and the design specs, never from raw REA
  output. Never paste the original's HTML, CSS, JS, decompiled code, SVGs,
  images or fonts. Never load from its domain or CDN.
- **Your words.** Labels, empty states and emails are written fresh. Matching
  what a button does is parity. Matching its sentence is copying.
- **Tokens only.** No raw hex or pixel values in components.

## Step 1: design tokens

Measure from the reference screenshots. Do not guess:

- **Colour roles**, not colours: bg, surface, border, text, text-muted, accent,
  on-accent, danger, success, warning. Usually 5 to 7 greys.
- **Type scale**: sizes, line heights, weights. Font category, not the file.
  Licensed font: pick an open one with the same job.
- **Spacing** (4 or 8 base), **radius**, **shadow**, **motion**, **layout**
  (max width, breakpoints, sidebar, header).

In mode B, an asset catalog or stylesheet (`inspect_asset_catalog`, the
bundle's CSS) can confirm measured values. Get them the same way as any other
REA question (see "Stuck" below): as numbers, not files. Icons come from an
open set (Lucide, Phosphor, SF Symbols).

Fill `tokens.json`, add a `pairs` list for every text/background combination,
run `contrast.py`. Zero AA failures (4.5:1 body, 3:1 large text and UI
borders). Fix in the tokens.

## Step 2: primitives

`components.md`: one block per component with variants, sizes, states
(including focus-visible, disabled, loading, error), tokens, a11y, screens.
Build them once in isolation before any screen. Use an accessible base where
the stack has one.

## Step 3: shell and vertical slice

Routing for every screen (stubs fine), layout, tokens, primitives, seed data.
Then the core loop end to end before anything else. If the backend is not
ready, a fake data layer with the real function signatures.

## Step 4: screen by screen

In `architecture.md` order. Per screen:

1. Read its recon row: purpose, components, states, flows, evidence.
2. Look at the reference screenshot for layout and hierarchy, not pixels.
3. Build with primitives and real data.
4. Every state: empty, loading, filled, error, no permission, long content,
   mobile width.
5. Semantic markup, labels, keyboard reachable, visible focus, alt text.
6. Set its `features.csv` rows to `yes` or `partial` with a note.
7. Screenshot at the reference viewport into
   `reconstruct/clone-screens/S07.png` for reconstruct-diff.
8. One commit per screen.

Done per screen: every state, works at 390px and 1440px, keyboard-only
completes the flow, no console errors, no borrowed copy, matrix updated,
screenshot saved.

## Step 5: build log

`reconstruct/build-log.md`, one line per screen: ID, date, done or partial,
what is missing, what was harder than expected. Say so in chat when a feature
is bigger than it looked.

## Stuck on how something works

Mode A: go back to the original as a user (help article, walkthrough, the
user's account).

Mode B: do not open REA yourself. Hand the question to a separate subagent
that loads `reverse-engineer-anything` and returns only a behaviour note: what
happens, limits, edge cases, the Evidence ID. It returns no code, pseudocode,
strings or endpoint paths. Add the note to `recon.md`, then build from the
note. The agent writing the code never sees the raw output.

## Output

Tokens and contrast report, primitives, screens built, matrix updated,
screenshots saved, and a summary: screens done of total, must-haves done of
total, next. Then `/reconstruct-test`.
