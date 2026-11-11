import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestSessionTransitionBenchmark(unittest.TestCase):
    def test_timed_results_contribute_to_matching_checksums(self):
        benchmark = (REPO_ROOT / "bench" / "bench_session_transition.js").read_text(encoding="utf-8")
        workloads = {
            "Pos": ("baseline.calculateCompletedSession", "PomodoroCore.calculateCompletedSession"),
            "Obj": ("baseline.calculateCompletedSession", "PomodoroCore.calculateCompletedSession"),
        }

        for workload, transitions in workloads.items():
            with self.subTest(workload=workload):
                base_checksum = f"base{workload}Checksum"
                opt_checksum = f"opt{workload}Checksum"
                self.assertIn(
                    f"if ({base_checksum} !== {opt_checksum})",
                    benchmark,
                    f"{workload} benchmark does not compare baseline and optimized checksums",
                )
                for transition in transitions:
                    checksum = base_checksum if transition.startswith("baseline") else opt_checksum
                    self.assertIn(
                        f"{checksum} += transitionChecksum({transition}(",
                        benchmark,
                        f"{transition} result is not accumulated in {workload} benchmark",
                    )


if __name__ == "__main__":
    unittest.main()
