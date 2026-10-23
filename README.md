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
/plugin marketplace add lseng/reconstruct-skill
/plugin install reconstruct-skill@reconstruct-skill
```

That installs the six skills and registers the REA MCP server, which runs
`npx -y rea-agents@6.5.0 mcp`. npx fetches REA from npm the first time it
starts (a few hundred MB, cached after that). Restart Claude Code, then check:

```
claude mcp list        # plugin:reconstruct-skill:rea ... Connected
```

The skills show up as `/reconstruct-skill:reconstruct-recon` and so on. If you
already registered REA yourself with a different command, you will have two
copies of its tools: remove yours (`claude mcp remove rea`) or disable the
plugin's in `/mcp`.

From a clone instead, which gives plain `/reconstruct-recon`:

```bash
git clone https://github.com/lseng/reconstruct-skill
cp -r reconstruct-skill/reconstruct-* ~/.claude/skills/
claude mcp add -s user rea -- npx -y rea-agents@6.5.0 mcp
```

For mode B, also install REA's own skill, which these skills hand REA tool
choice to (the plugin does not ship it):

```bash
npx -y rea-agents@6.5.0 setup --skill-client claude_code --yes
```

Then check everything:

```bash
python3 reconstruct-skill/reconstruct-recon/doctor.py   # /reconstruct-recon runs this as step 0
```

### Requirements

- Python 3.8+ for the tools. Nothing to pip install. Mode A needs nothing else.
- Mode B: Node 22.19+, 24.11+ or 26+ with npx, for REA (`rea-agents` 6.5.0,
  pinned). The plugin starts it for you; a clone needs the `claude mcp add`
  line above.
- Optional, for native binaries: Ghidra 12.1 and Java 21. REA starts without
  them. When `GHIDRA_INSTALL_DIR` (and `JAVA_HOME` if Java is not on the
  path) is set in the shell that starts Claude Code, the REA server inherits
  it and uses Ghidra. With Homebrew:

  ```bash
  brew install ghidra openjdk@21
  export GHIDRA_INSTALL_DIR="$(brew --prefix ghidra)/libexec"
  ```

  Set it to a real absolute path or leave it unset: REA refuses to start
  when it is set to an empty or relative value. For a clone you can pin it on
  the server instead: `claude mcp add -s user rea -e GHIDRA_INSTALL_DIR=/path/to/ghidra -- npx -y rea-agents@6.5.0 mcp`.
- If npx cannot fetch from your npm registry (a private mirror that needs a
  login, for example), `doctor.py` says so. Log in to it, or point npm at
  `https://registry.npmjs.org/`.

## The tools

All standard-library Python. Only `doctor.py` touches the network, when it
starts REA through npx (`--offline` skips that).

```bash
python3 reconstruct-diff/parity.py reconstruct/features.csv --require-evidence  # parity + evidence gaps
python3 reconstruct-diff/imgdiff.py original.png rebuild.png --out diff.png     # layout diff, ignores colour
python3 reconstruct-build/contrast.py reconstruct/design/tokens.json            # WCAG contrast on tokens
python3 reconstruct-sweep/sweep.py . --config reconstruct/sweep.json            # anything of the original left?
python3 reconstruct-recon/doctor.py                                             # node, npx, REA MCP, REA skill, Ghidra
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
(`rea-agents`, MIT) is not bundled: the plugin's MCP entry runs it from npm
at runtime, and none of its code is in this repo. See `NOTICE`.

Not legal advice. Before mode B on anything you do not own, check the licence
and get a real answer on whether you may reverse engineer it.
