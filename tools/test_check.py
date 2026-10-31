import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check  # noqa: E402


class SummarizeTest(unittest.TestCase):
    def test_all_pass(self):
        self.assertEqual(check.summarize(20, [], []), "20/20 steps pass")

    def test_skips_are_not_counted_as_passes(self):
        self.assertEqual(
            check.summarize(20, [], ["17-tls-handshake", "18-https-server", "19-certificates"]),
            "17/20 steps pass, 3 skipped",
        )

    def test_failures_are_named_in_the_tail(self):
        self.assertEqual(
            check.summarize(20, ["05-http-request"], ["17-tls-handshake"]),
            "18/20 steps pass, 1 skipped, 1 failed",
        )


if __name__ == "__main__":
    unittest.main()
