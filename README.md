# reconstruct-skill

Six Claude skills that rebuild an app from evidence, not from guesses.

It combines two tools. [Replica](https://github.com/Jakeschincariol/replica-skill)
supplies the pipeline: recon, architecture, build, test, parity diff, and the
stdlib Python tools for scoring and sweeping. [REA](https://github.com/morluto/rea)
supplies the evidence: decompilation, bundle analysis and runtime captures of
the shipped artifact, each result tied to an Evidence ID.

Recon works in two tiers:

- **Mode A, public only (the default).** Help docs, store listings, screenshots,
  public API docs, and the user's own account. This is Replica's clean-room method.
- **Mode B, authorized artifact.** Everything in A, plus REA on the shipped
  artifact. Only with a stated basis recorded in `reconstruct/scope.md`: we
  own it, written authorization, an open-source licence, or another legal
  basis the user confirms.

In both modes evidence describes behaviour and never becomes code.
`/reconstruct-sweep` checks that before anything ships.

## The six

| command | what it does |
| --- | --- |
| `/reconstruct-recon` | Scope, evidence mode, screens, flows, components, data model and `features.csv`, every row citing a URL or a REA Evidence ID. |
| `/reconstruct-architect` | Stack, schema, API and build order. Evidence-backed data shapes first. |
| `/reconstruct-build` | Design tokens with a WCAG check, primitives, the vertical slice, then every screen with every state. |
| `/reconstruct-test` | Test plan from the flows, Playwright specs, bug reports. In mode B, REA captures of the original are the oracle. |
| `/reconstruct-diff` | Weighted parity with an evidence report, a colour-blind layout diff, and REA behavioural verification in mode B. |
| `/reconstruct-sweep` | The ship gate: the original's identity, and in mode B, identifiers from the evidence that would mean code leaked in. |

```
recon -> architect -> build -> test -> diff -> sweep
```

Each reads what the last wrote, in a `reconstruct/` folder in your project.

## Install

As a plugin in Claude Code:

```
/plugin marketplace add <this repo's git URL or local path>
/plugin install reconstruct-skill@reconstruct-skill
```

They show up as `/reconstruct-skill:reconstruct-recon` and so on. To get plain
`/reconstruct-recon` instead, copy the folders:

```bash
cp -r reconstruct-* ~/.claude/skills/
```

### Requirements

- Python 3.8+ for the tools. Nothing to pip install.
- Mode B only: the REA MCP server and its `reverse-engineer-anything` skill.
  Written against `rea-agents` 6.5.0. Check with `rea --version`. These skills
  hand all REA tool choice, setup and recovery to that skill and do not copy it.

## The tools

All standard-library Python, none touch the network.

```bash
python3 reconstruct-diff/parity.py reconstruct/features.csv --require-evidence  # parity + evidence gaps
python3 reconstruct-diff/imgdiff.py original.png rebuild.png --out diff.png     # layout diff, ignores colour
python3 reconstruct-build/contrast.py reconstruct/design/tokens.json            # WCAG contrast on tokens
python3 reconstruct-sweep/sweep.py . --config reconstruct/sweep.json            # anything of the original left?
```

What changed from Replica's versions:

- `parity.py` reads optional `evidence` and `confidence` columns. It reports
  the split between artifact evidence (REA `ev_` IDs), public evidence (URLs)
  and none, and flags must-haves that are only a guess. `--require-evidence`
  exits 1 while any counted row has no evidence.
- `sweep.py` skips the `reconstruct/` planning folder (`--include-plan` to
  check it). The skill uses it a second way: as a clean-room check that feeds
  in internal identifiers and endpoint paths from the REA evidence.

```bash
python3 -m unittest discover -s tests -v
```

## Credit and licence

MIT. Pipeline, templates and `imgdiff.py`, `parity.py`, `sweep.py`,
`contrast.py` are adapted from Replica by Jake Schincariol (MIT). REA
(`rea-agents`, MIT) is a separate install and is not bundled. See `NOTICE`.

Not legal advice. Before mode B on anything you do not own, check the licence
and get a real answer on whether you may reverse engineer it.
