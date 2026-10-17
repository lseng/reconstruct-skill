---
name: reconstruct-recon
description: >-
  Maps an app for a rebuild: screen inventory, user flows, components, data
  model and an evidence-backed feature matrix. Two evidence tiers: public
  sources and the user's own account always (tier A), plus REA analysis of the
  shipped artifact when the user states an authorization basis (tier B). Every
  row cites a URL or a REA Evidence ID. The first step of the reconstruct pack.
  Use when the user says "rebuild this app", "reconstruct X", "map out X",
  "what screens and flows does X have", "reverse engineer X so we can rebuild
  it", or hands over an app URL, store link, IPA, APK, ASAR or binary to rebuild.
---

# reconstruct-recon

Everything else in the pack builds from what this skill writes. Output goes in
the user's project:

```
reconstruct/scope.md       target, slice, evidence mode and its basis (template: scope.md)
reconstruct/recon.md       the recon map (template: recon-map.md)
reconstruct/features.csv   the feature matrix (template: features.csv)
reconstruct/screens/       reference screenshots of the original. Never shipped.
```

## The rules, before anything else

- **Pick the mode in writing.** Tier A is the default. Tier B needs a basis the
  user states (we own it, written authorization, an open-source licence, or
  another legal basis they confirm) recorded in `scope.md`. Do not infer
  authorization from the user having a copy installed. Many licences forbid
  reverse engineering, so read the EULA or terms and record what they say. If
  the basis is unclear, stay in tier A and say why.
- **Clean room in both tiers.** Evidence describes behaviour. It never becomes
  code. Do not paste decompiled code, bundle code, assets, strings, copy or a
  third party's private endpoints into the rebuild or into specs the build
  reads verbatim. Write behaviour in your own words.
- **Reading, not scraping.** No crawlers or bulk downloads against sites. Read
  pages at human speed. The user drives their own account.
- **Never someone else's account**, never a password, never past a paywall.
- **Screenshots are reference.** They stay in `reconstruct/screens/`.

## Step 1: scope and mode

Ask, or propose answers and get a yes:

1. **Which app, which platform**, and for tier B the exact artifact (path,
   version). If the user says only "my app", ask which one.
2. **Which slice.** Default to the core loop, the one flow users pay for.
3. **Who it is for.**
4. **Mode and basis.** Fill `scope.md`.

## Step 2: tier A sources

Build a sources table first, a URL on every row:

| source | what it gives you |
| --- | --- |
| help center / docs | the most complete feature list, and the settings |
| pricing page | which features matter (they gate them) |
| changelog | what was added recently |
| app store listing | screenshots of key screens, the pitch |
| public walkthrough videos | real flows, click by click |
| the user's own account | every state, driven by the user |
| public API docs | the data model, almost for free |

## Step 3: tier B evidence (mode B only)

Load the `reverse-engineer-anything` skill and follow its routing. Do not
duplicate its instructions here. It owns tool choice, setup and recovery. The
usual entry points by target:

| target | first REA tool |
| --- | --- |
| ASAR, extracted JS or Electron tree | `analyze_javascript_application` (`detail: "summary"` when large) |
| web app the user has open | `list_browser_targets`, then `capture_browser_scenario` for a declared flow |
| IPA / macOS app | `open_binary`, then `project_apple_application_graph`, `analyze_swift_types` |
| APK | `inspect_android_package`, then `project_android_application_graph` |
| native binary | `open_binary`, then `binary_overview` and focused analysis |

What to pull out, for each, with the Evidence ID:

- **Features and routes** the public sources missed (feature flags, hidden
  settings, routes). Trace a seed with `trace_application_feature`.
- **Data shapes**: persisted models, schemas, SQLite stores
  (`inspect_sqlite_database`), request and response shapes from a capture.
- **State machines and edge cases**: error branches, limits, retries.
- **Unknowns**: anything REA could not settle goes in the Unknowns table and,
  for tracked work, `record_unknown`.

Keep REA's distinction between observed, derived and inferred. Static
analysis never proves something ran.

## Step 4: screen inventory

One row per screen, stable IDs S01, S02... Every other file refers to them.
Record states: empty, loading, filled, error, permission denied, mobile. Each
row cites its evidence and confidence.

## Step 5: user flows

F01, F02... a goal and the screens it passes through, edge cases, happy-path
click count (the number to beat), evidence, confidence.

## Step 6: components

Every repeated UI part: name, variants, states, screens. This becomes the
build's component list.

## Step 7: data model

Entities, fields and relationships, each with evidence and confidence. Tier B
evidence outranks tier A inference. When they disagree, record both and the
contradiction.

## Step 8: feature matrix

Write `reconstruct/features.csv`: `feature, area, priority, original, clone,
notes, evidence, confidence`. Priority is must / should / could. `clone`
starts at `no`. `evidence` is `;`-separated URLs or `ev_` IDs. A must-have
that is only a `guess` gets a probe in Unknowns before anyone builds it.

Check it:

```bash
python3 ../reconstruct-diff/parity.py reconstruct/features.csv
```

The Evidence section lists rows with none.

## Step 9: what cannot be rebuilt

`skip` rows with a reason: licensed content, the network and its users, data
the app owns, partner deals, hardware, regulated licences.

## Step 10: size it

Screens, flows, entities, the hard parts (realtime, sync, payments, calendar
or email integrations, offline). Size: S (a weekend), M (a few weeks), L (a
quarter), XL (rescope). No promises of a perfect rebuild.

## Output

`scope.md`, `recon.md`, `features.csv`, then a summary: mode, the core loop,
screen and flow counts, evidence split (artifact / public / none), the three
hardest parts, open unknowns, out of scope, and the next step:
`/reconstruct-architect`.
