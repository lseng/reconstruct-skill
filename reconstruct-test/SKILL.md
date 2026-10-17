---
name: reconstruct-test
description: >-
  Tests the rebuild flow by flow: a test plan from the recon flows with happy
  paths, edge and negative cases, Playwright end-to-end specs, a manual pass
  for the rest, and bug reports with severity and evidence. In mode B, REA
  captures of the original act as the behaviour oracle. Use when the user says
  "test the rebuild", "find bugs", "QA this", "write e2e tests", "does it
  work", or after /reconstruct-build.
---

# reconstruct-test

Reads the flows in `reconstruct/recon.md`. Writes `reconstruct/test-plan.md`,
`reconstruct/bugs.md`, and specs in the project (`e2e/`). Templates here:
`test-plan.md`, `bug-report.md`, `e2e.example.spec.ts`.

Read `reconstruct/scope.md` first. REA is used only if it records mode B with
a ticked basis. If it is missing or has no basis, work in mode A and say so.

## The rule

**Test the rebuild, not the original.** Never load-test, fuzz or script
against the original's servers. Observing the original is allowed: by hand in
mode A, and through declared REA scenarios on the authorized artifact in mode
B.

## Step 1: the plan

For every flow F01, F02...:

- **Happy path**: steps and the expected end state.
- **Edge cases** that apply: empty input, very long input, emoji and accents,
  two tabs, double submit, back and refresh mid-flow, slow or offline network,
  expired session, a second user's data (must be invisible), time zones and
  DST, mobile width, keyboard only, screen reader labels.
- **Negative cases**: wrong password, card declined (Stripe `4000 0000 0000
  0002`), permission denied, deleted record.
- Edge cases REA found in the original (error branches, limits, retries),
  each with its Evidence ID.

Number every case: F01-H1, F01-E3, F01-N2.

## Step 2: the oracle (mode B)

For each must-have flow, capture the original doing it once with a declared
scenario (`capture_browser_scenario`, `capture_native_ui_scenario` or
`capture_process_scenario` via `reverse-engineer-anything`). Record the
Evidence ID next to the case. That capture is what "expected" means. It is
also the left side of the behaviour diff in `/reconstruct-diff`.

Clean room applies to tests too. Write expected outcomes as behaviour ("a
second booking for the slot is refused with a visible error"). Do not paste
captured responses, payloads or the original's data into fixtures or seed
data.

## Step 3: automate

Playwright, one spec per flow, against the local dev server with seed data.
Role and label selectors, never CSS classes (see `e2e.example.spec.ts`). Every
spec fails on console errors and 5xx responses, and runs an axe scan per
screen.

```bash
npm i -D @playwright/test && npx playwright install chromium
npx playwright test
```

## Step 4: click through the rest

Emails, real OAuth, payments end to end, visual glitches: a manual pass,
driving the local rebuild with a browser tool where available, a screenshot
per step. Otherwise give the user the checklist and wait.

## Step 5: report bugs

`reconstruct/bugs.md` in the `bug-report.md` format: ID, severity, steps,
expected, actual, evidence.

| | means |
| --- | --- |
| S1 | data loss, security hole, payments wrong, core flow blocked |
| S2 | a feature broken, no workaround |
| S3 | broken with a workaround, or visibly wrong |
| S4 | cosmetic |

Only reproduced bugs. "Might be" goes in a "to check" list.

## Step 6: fix loop

S1 and S2 first. Failing test first, fix, watch it pass, keep the test. Re-run
the suite after each batch. Record the fixing commit in `bugs.md`.

## Output

`test-plan.md`, specs, `bugs.md`, and a summary: cases run, passed, failed,
bugs by severity, fixed. Nothing ships with an open S1. Next:
`/reconstruct-diff`.
