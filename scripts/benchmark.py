"""Measure dependency-free CLI startup with a reproducible local command."""

from __future__ import annotations

import os
import statistics
import subprocess
import sys
import time
from pathlib import Path


def run_once(environment: dict[str, str]) -> float:
    started = time.perf_counter()
    subprocess.run(
        [sys.executable, "-m", "oss_link_auditor.cli", "--help"],
        check=True,
        env=environment,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return (time.perf_counter() - started) * 1000


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")
    for _ in range(3):
        run_once(environment)
    timings = [run_once(environment) for _ in range(20)]
    print(f"python={sys.version.split()[0]}")
    print(f"runs={len(timings)}")
    print(f"median_ms={statistics.median(timings):.2f}")
    print(f"p95_ms={sorted(timings)[18]:.2f}")


if __name__ == "__main__":
    main()
