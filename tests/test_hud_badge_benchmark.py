import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestHUDBadgeBenchmark(unittest.TestCase):
    def test_timed_badge_results_contribute_to_matching_checksums(self):
        benchmark = (REPO_ROOT / "bench" / "bench_hud_badge.js").read_text(encoding="utf-8")
        workloads = {
            "HUD": ("baselineFormatStreakBadge", "PomodoroCore.formatStreakBadge",
                    "baselineFormatFocusTimeBadge", "PomodoroCore.formatFocusTimeBadge"),
            "Streak": ("baselineFormatStreakBadge", "PomodoroCore.formatStreakBadge"),
            "Focus": ("baselineFormatFocusTimeBadge", "PomodoroCore.formatFocusTimeBadge"),
            "Mixed": ("baselineFormatStreakBadge", "PomodoroCore.formatStreakBadge",
                      "baselineFormatFocusTimeBadge", "PomodoroCore.formatFocusTimeBadge"),
        }

        for workload, formatters in workloads.items():
            with self.subTest(workload=workload):
                base_checksum = f"base{workload}Checksum"
                opt_checksum = f"opt{workload}Checksum"
                self.assertIn(
                    f"if ({base_checksum} !== {opt_checksum})",
                    benchmark,
                    f"{workload} benchmark does not compare baseline and optimized checksums",
                )
                for formatter in formatters:
                    checksum = base_checksum if formatter.startswith("baseline") else opt_checksum
                    self.assertIn(
                        f"{checksum} += badgeChecksum({formatter}(",
                        benchmark,
                        f"{formatter} result is not accumulated in {workload} benchmark",
                    )


if __name__ == "__main__":
    unittest.main()
