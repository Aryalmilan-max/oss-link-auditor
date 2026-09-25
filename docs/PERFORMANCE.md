# Performance budget

Measure before optimizing. The current launch budget is:

- CLI `--help` median startup below 150 ms on a contemporary developer laptop.
- deterministic demo completes below 10 seconds.
- no runtime dependencies and no background process or telemetry.

Reproduce the startup benchmark from the repository root:

```bash
python3 scripts/benchmark.py
```

The script performs 3 warmups and 20 measured subprocess launches, then prints
the median and p95. Results depend on hardware, OS, Python build, and system
load; never compare results without recording that context.

## Verified launch baseline

Measured 2026-09-25 on arm64 macOS 26.6.2 with Python 3.14.6:

- CLI startup median: 113.77 ms over 20 runs
- CLI startup p95: 120.75 ms
- deterministic demo wall time: 0.65 seconds (`/usr/bin/time -p`)

These are local verification results, not universal performance claims.
