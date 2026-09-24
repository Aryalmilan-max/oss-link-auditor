"""Command-line interface for oss-link-auditor."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .core import audit_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-link-auditor",
        description="Audit HTTP links in Markdown without weakening TLS verification.",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Return a non-zero exit code when broken or unreachable links are found.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    result = audit_paths(args.paths, workers=args.workers, timeout=args.timeout)

    if args.as_json:
        print(
            json.dumps(
                {
                    "files": result.files,
                    "checked": len(result.links),
                    "failures": [asdict(link) for link in result.failures],
                    "redirects": [asdict(link) for link in result.redirects],
                },
                indent=2,
            )
        )
    else:
        for link in (*result.failures, *result.redirects):
            status = link.status if link.status is not None else "ERROR"
            detail = link.error or link.destination or ""
            print(f"{status}\t{link.url}\t{detail}")
        print(
            f"Checked {len(result.links)} unique links in {len(result.files)} Markdown files; "
            f"{len(result.failures)} failures, {len(result.redirects)} redirects."
        )

    return 1 if args.fail_on_broken and result.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
