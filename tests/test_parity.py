import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from _load import load, ROOT

parity = load("reconstruct-diff", "parity")

MATRIX = """feature,area,priority,original,clone,notes
Pick a time slot,booking page,must,yes,yes,
Confirmation email,booking page,must,yes,partial,no calendar file yet
Reschedule link,booking page,must,yes,no,
Round-robin across a team,team,should,yes,no,
Custom booking questions,booking page,should,yes,yes,
Embed on a website,sharing,could,yes,no,
Their partner marketplace,integrations,could,yes,skip,their network not ours
SMS reminders,notifications,should,no,yes,ours: the top request in reviews
"""


def write(d, name, text):
    path = os.path.join(d, name)
    with open(path, "w") as fh:
        fh.write(text)
    return path


class Score(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = write(self.tmp.name, "features.csv", MATRIX)

    def tearDown(self):
        self.tmp.cleanup()

    def test_weighted_score(self):
        r = parity.score(parity.load(self.path))
        # counted weights: 3+3+3+2+2+1 = 14, earned: 3 + 1.5 + 0 + 0 + 2 + 0 = 6.5
        self.assertAlmostEqual(r["feature_score"], round(100 * 6.5 / 14, 1))
        self.assertEqual(r["counted"], 6)
        self.assertEqual((r["must_have_done"], r["must_have_total"]), (1, 3))

    def test_skip_and_extras_are_not_scored_but_listed(self):
        r = parity.score(parity.load(self.path))
        self.assertEqual([m["feature"] for m in r["skipped"]], ["Their partner marketplace"])
        self.assertEqual([m["feature"] for m in r["extras"]], ["SMS reminders"])

    def test_missing_is_in_build_order(self):
        r = parity.score(parity.load(self.path))
        order = [m["feature"] for m in r["missing"]]
        self.assertEqual(order[0], "Reschedule link")          # must, not started
        self.assertEqual(order[1], "Confirmation email")       # must, partial
        self.assertEqual(order[2], "Round-robin across a team")
        self.assertEqual(order[-1], "Embed on a website")
        self.assertEqual(r["missing"][0]["priority"], "must")

    def test_weakest_area_first(self):
        r = parity.score(parity.load(self.path))
        self.assertEqual(r["by_area"][0]["score"], 0.0)
        self.assertIn(r["by_area"][0]["area"], ("team", "sharing"))

    def test_render_says_not_shippable(self):
        r = parity.combine(parity.score(parity.load(self.path)), [])
        text = parity.render(r)
        self.assertIn("Not shippable yet: 2 must-have", text)
        self.assertIn("their network not ours", text)

    def test_visual_folds_in_at_20_percent(self):
        d = self.tmp.name
        v1 = write(d, "a.json", json.dumps({"score": 80.0, "mode": "layout",
                                            "files": {"clone": "clone/home.png"}}))
        v2 = write(d, "b.json", json.dumps({"score": 60.0, "mode": "layout"}))
        r = parity.combine(parity.score(parity.load(self.path)),
                           parity.visual_scores([v1, v2]))
        self.assertEqual(r["layout_score"], 70.0)
        self.assertAlmostEqual(r["overall"], round(0.8 * r["feature_score"] + 14.0, 1))

    def test_bad_values_are_reported_not_fatal(self):
        p = write(self.tmp.name, "bad.csv",
                  "feature,priority,clone\nThing,urgent,maybe\n")
        r = parity.score(parity.load(p))
        self.assertEqual(len(r["problems"]), 3)   # priority, clone, no evidence column
        self.assertTrue(any("no 'evidence' column" in x for x in r["problems"]))
        self.assertEqual(r["feature_score"], 0.0)

    def test_missing_column_is_an_error(self):
        p = write(self.tmp.name, "nocol.csv", "feature,area\nx,y\n")
        with redirect_stderr(io.StringIO()):
            self.assertEqual(parity.main([p]), 2)

    def test_cli_fail_under(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main([self.path, "--fail-under", "80"]), 1)
            self.assertEqual(parity.main([self.path, "--fail-under", "10"]), 0)

    def test_evidence_tiers_and_gaps(self):
        ev = "ev_" + "a" * 64
        p = write(self.tmp.name, "ev.csv",
                  "feature,priority,original,clone,evidence,confidence\n"
                  "A,must,yes,yes,%s,observed\n"
                  "B,must,yes,no,https://help.example.com/b,guess\n"
                  "C,should,yes,no,,inferred\n"
                  "D,could,no,yes,,\n" % ev)
        r = parity.score(parity.load(p))
        self.assertEqual(r["evidence"]["tiers"], {"artifact": 1, "public": 1, "none": 1})
        self.assertEqual(r["evidence"]["unsupported"], ["C"])   # D is an extra, not counted
        self.assertEqual(r["evidence"]["guessed_musts"], ["B"])
        self.assertEqual(r["problems"], [])

    def test_malformed_evidence_id_and_confidence_are_problems(self):
        p = write(self.tmp.name, "bad-ev.csv",
                  "feature,priority,clone,evidence,confidence\n"
                  "A,must,yes,ev_123,sure\n")
        r = parity.score(parity.load(p))
        self.assertEqual(len(r["problems"]), 2)
        self.assertEqual(r["evidence"]["tiers"], {"artifact": 0, "public": 0, "none": 1})
        self.assertEqual(r["evidence"]["unsupported"], ["A"])

    def test_junk_evidence_does_not_satisfy_require_evidence(self):
        junk = ["TODO", "ev_BAD", "EV_" + "a" * 64, "see notes", "ev_" + "A" * 64]
        rows = "".join("R%d,must,yes,%s\n" % (i, t) for i, t in enumerate(junk))
        p = write(self.tmp.name, "junk.csv", "feature,priority,clone,evidence\n" + rows)
        r = parity.score(parity.load(p))
        self.assertEqual(r["evidence"]["tiers"]["none"], len(junk))
        self.assertEqual(len(r["problems"]), len(junk))
        with redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main([p, "--require-evidence"]), 1)

    def test_one_valid_token_backs_the_row(self):
        p = write(self.tmp.name, "mixed.csv",
                  "feature,priority,clone,evidence\nA,must,yes,TODO;https://x.test/a\n")
        r = parity.score(parity.load(p))
        self.assertEqual(r["evidence"]["tiers"]["public"], 1)
        self.assertEqual(len(r["problems"]), 1)

    def test_missing_column_is_one_line_not_a_flood(self):
        r = parity.combine(parity.score(parity.load(self.path)), [])
        text = parity.render(r)
        self.assertIn("no evidence column", text)
        self.assertNotIn("- no evidence: ", text)

    def test_cli_require_evidence(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main([self.path, "--require-evidence"]), 1)
        p = write(self.tmp.name, "full.csv",
                  "feature,priority,clone,evidence\nA,must,yes,https://x.test/a\n")
        with redirect_stdout(io.StringIO()):
            self.assertEqual(parity.main([p, "--require-evidence"]), 0)

    def test_shipped_template_parses(self):
        path = os.path.join(ROOT, "reconstruct-recon", "features.csv")
        r = parity.score(parity.load(path))
        self.assertGreater(r["counted"], 0)
        self.assertEqual(r["problems"], [])


if __name__ == "__main__":
    unittest.main()
