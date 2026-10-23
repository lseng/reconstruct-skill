#!/usr/bin/env python3
"""Setup check for the reconstruct pack. Standard library only.

Reports what is present and what is missing, with the command that fixes each
gap. Tier A needs only Python. Tier B also needs Node, npx and the REA MCP
server, and is better with REA's own skill and Ghidra.

    python3 doctor.py              # everything, including a live REA MCP check
    python3 doctor.py --offline    # skip the REA check (it may fetch rea-agents from npm)

The REA check starts the same server the plugin registers
(npx -y rea-agents@6.5.0 mcp) through REA's own "mcp doctor" and reads its
verdict. It inherits this shell's GHIDRA_INSTALL_DIR and JAVA_HOME, as the
plugin's server does.

Exit code 1 when anything tier B needs is missing. Optional items never fail it.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

REA = "rea-agents@6.5.0"
GHIDRA_BREW = "/opt/homebrew/opt/ghidra/libexec"

FIX = {
    "python": "Install Python 3.8 or newer: https://www.python.org/downloads/",
    "node": "brew install node   (or https://nodejs.org, version 22.19+, 24.11+ or 26+)",
    "rea": "claude mcp add -s user rea -- npx -y %s mcp   (plugin installs already register it; "
           "run /mcp to see why it failed)" % REA,
    "npm": "npm config get registry   (npx fetches rea-agents from it; log in to it, or use "
           "npm_config_registry=https://registry.npmjs.org/)",
    "skill": "npx -y %s setup --skill-client claude_code --yes" % REA,
    "ghidra": "brew install ghidra && export GHIDRA_INSTALL_DIR=\"$(brew --prefix ghidra)/libexec\""
              "   (Linux: unzip a release from github.com/NationalSecurityAgency/ghidra/releases "
              "and point GHIDRA_INSTALL_DIR at it)",
    "java": "brew install openjdk@21 && export JAVA_HOME=\"$(brew --prefix openjdk@21)/libexec/"
            "openjdk.jdk/Contents/Home\"",
}


def node_supported(version):
    """REA's engines field: ^22.19.0 || ^24.11.0 || >=26.0.0."""
    m = re.match(r"v?(\d+)\.(\d+)", version or "")
    if not m:
        return False
    major, minor = int(m.group(1)), int(m.group(2))
    return (major == 22 and minor >= 19) or (major == 24 and minor >= 11) or major >= 26


def run(cmd, timeout):
    try:
        out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             universal_newlines=True, timeout=timeout)
        return out.returncode, out.stdout, out.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        return None, "", str(exc)


def skill_dirs():
    dirs = [os.path.join(".claude", "skills"), os.path.expanduser("~/.claude/skills"),
            os.path.expanduser("~/.agents/skills")]
    if os.environ.get("CLAUDE_CONFIG_DIR"):
        dirs.insert(1, os.path.join(os.environ["CLAUDE_CONFIG_DIR"], "skills"))
    return dirs


def check_python():
    v = sys.version_info
    return ("python", "need", v >= (3, 8), "Python %d.%d.%d" % (v[0], v[1], v[2]))


def check_node():
    node = shutil.which("node")
    if not node:
        return ("node", "mode B", False, "node not found")
    _, out, _ = run([node, "--version"], 20)
    version = out.strip()
    if not node_supported(version):
        return ("node", "mode B", False, "node %s is older than REA supports" % (version or "?"))
    return ("node", "mode B", True, "node %s" % version)


def check_npx():
    found = shutil.which("npx")
    return ("node", "mode B", bool(found), "npx %s" % ("at " + found if found else "not found"))


def check_rea(offline):
    if offline:
        return ("rea", "mode B", None, "REA MCP check skipped (--offline)")
    if not shutil.which("npx"):
        return ("rea", "mode B", False, "REA MCP not checked: npx not found")
    code, out, err = run(["npx", "-y", REA, "mcp", "doctor", "--json"], 300)
    try:
        report = json.loads(out[out.find("{"):])
        if not isinstance(report, dict):
            raise ValueError
    except ValueError:
        npm = [l[len("npm error "):] for l in err.splitlines() if l.startswith("npm error ")]
        if npm:
            return ("npm", "mode B", False, "npx could not fetch %s: %s"
                    % (REA, "; ".join(npm[:2])))
        detail = (err or out).strip().splitlines()
        return ("rea", "mode B", False, "REA MCP did not start: %s"
                % (detail[-1] if detail else "exit %s" % code))
    if report.get("healthy"):
        tools = ((report.get("inventory") or {}).get("tools") or {}).get("observed")
        version = (report.get("server") or {}).get("version")
        return ("rea", "mode B", True, "REA MCP %s starts, %s tools" % (version, tools))
    stderr = ((report.get("diagnostics") or {}).get("stderr") or "").strip()
    return ("rea", "mode B", False, "REA MCP unhealthy: %s" % (stderr or "see npx -y %s mcp doctor" % REA))


def check_skill():
    for d in skill_dirs():
        if os.path.isfile(os.path.join(d, "reverse-engineer-anything", "SKILL.md")):
            return ("skill", "mode B", True, "REA skill in %s" % d)
    return ("skill", "mode B", False, "REA's reverse-engineer-anything skill not found")


def check_ghidra():
    path = os.environ.get("GHIDRA_INSTALL_DIR")
    if path is None:
        hint = " (one is at %s)" % GHIDRA_BREW if os.path.isdir(GHIDRA_BREW) else ""
        return ("ghidra", "optional", False, "GHIDRA_INSTALL_DIR not set%s; native "
                "decompilation falls back to Hopper or IDA if present" % hint)
    if not path or not os.path.isabs(path):
        return ("ghidra", "optional", False, "GHIDRA_INSTALL_DIR must be absolute; REA will "
                "refuse to start with %r" % path)
    if not os.path.isfile(os.path.join(path, "support", "analyzeHeadless")):
        return ("ghidra", "optional", False, "no support/analyzeHeadless under %s" % path)
    return ("ghidra", "optional", True, "Ghidra at %s" % path)


def check_java():
    home = os.environ.get("JAVA_HOME")
    if home and os.path.isfile(os.path.join(home, "bin", "java")):
        return ("java", "optional", True, "Java at %s" % home)
    if home:
        return ("java", "optional", False, "JAVA_HOME=%s has no bin/java" % home)
    java = shutil.which("java")
    if java and run([java, "-version"], 20)[0] == 0:
        return ("java", "optional", True, "java on PATH (Ghidra needs 21+)")
    return ("java", "optional", False, "no Java found (Ghidra needs it)")


def checks(offline=False):
    return [check_python(), check_node(), check_npx(), check_rea(offline),
            check_skill(), check_ghidra(), check_java()]


def report(results):
    lines, fixes = [], []
    for key, level, ok, detail in results:
        mark = "ok" if ok else ("skip" if ok is None else "MISSING")
        lines.append("%-8s %-11s %s" % (mark, "[%s]" % level, detail))
        if ok is False and FIX[key] not in fixes:
            fixes.append(FIX[key])
    if fixes:
        lines.append("")
        lines.append("To fix:")
        lines.extend("  " + f for f in fixes)
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--offline", action="store_true", help="skip the live REA MCP check")
    args = ap.parse_args(argv)
    results = checks(args.offline)
    print(report(results))
    failed = [r for r in results if r[1] in ("need", "mode B") and r[2] is False]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
