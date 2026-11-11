import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestVolumeBenchmark(unittest.TestCase):
    def test_timed_results_contribute_to_matching_checksums(self):
        benchmark = (REPO_ROOT / "bench" / "bench_volume.js").read_text(encoding="utf-8")
        workloads = {
            "Slider": ("baselineFormatVolumePercent", "baselineGetVolumeIcon",
                       "PomodoroCore.formatVolumePercent", "PomodoroCore.getVolumeIcon"),
            "Mixed": ("baselineFormatVolumePercent", "baselineGetVolumeIcon",
                      "PomodoroCore.formatVolumePercent", "PomodoroCore.getVolumeIcon"),
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
                        f"{checksum} += volumeChecksum({formatter}(",
                        benchmark,
                        f"{formatter} result is not accumulated in {workload} benchmark",
                    )


if __name__ == "__main__":
    unittest.main()
