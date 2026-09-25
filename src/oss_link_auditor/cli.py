"""Command-line interface for OSS Link Auditor."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .core import AuditResult, LinkResult, audit_paths


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oss-link-auditor",
        description="Audit HTTP(S) links in Markdown with source-aware trust reports.",
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Markdown files or directories")
    parser.add_argument("--workers", type=positive_int, default=12)
    parser.add_argument("--timeout", type=positive_float, default=15.0)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    output.add_argument("--markdown", action="store_true", help="Emit a Markdown trust report")
    parser.add_argument(
        "--fail-on-broken",
        action="store_true",
        help="Exit 1 when broken, unreachable, or blocked links exist",
    )
    parser.add_argument(
        "--allow-private",
        action="store_true",
        help="Allow private/loopback targets; use only for trusted internal documentation",
    )
    return parser


def summary(result: AuditResult) -> dict[str, int]:
    counts = {
        name: 0 for name in ("HEALTHY", "REDIRECT", "REDIRECT-CROSS-HOST", "BROKEN", "BLOCKED")
    }
    for link in result.links:
        counts[link.category] += 1
    return {"files": len(result.files), "links": len(result.links), **counts}


def link_payload(link: LinkResult) -> dict[str, object]:
    return {
        "url": link.url,
        "status": link.status,
        "destination": link.destination,
        "error": link.error,
        "category": link.category,
        "sources": [{"path": source.path, "line": source.line} for source in link.sources],
    }


def render_json(result: AuditResult) -> str:
    return json.dumps(
        {
            "summary": summary(result),
            "files": list(result.files),
            "links": [link_payload(link) for link in result.links],
        },
        indent=2,
        sort_keys=True,
    )


def escape_cell(value: object) -> str:
    return str(value if value is not None else "—").replace("|", "\\|").replace("\n", " ")


def location(link: LinkResult) -> str:
    if not link.sources:
        return "—"
    first = link.sources[0]
    extra = len(link.sources) - 1
    return f"{first.path}:{first.line}" + (f" (+{extra})" if extra else "")


def render_markdown(result: AuditResult) -> str:
    counts = summary(result)
    lines = [
        "## OSS Link Auditor trust report",
        "",
        f"Scanned **{counts['files']}** Markdown file(s) and **{counts['links']}** unique link(s).",
        "",
        f"- Healthy: {counts['HEALTHY']}",
        f"- Redirects: {counts['REDIRECT'] + counts['REDIRECT-CROSS-HOST']}",
        f"- Broken: {counts['BROKEN']}",
        f"- Blocked for safety: {counts['BLOCKED']}",
    ]
    findings = [link for link in result.links if link.category != "HEALTHY"]
    if not findings:
        return "\n".join(lines + ["", "✅ No findings require review."])
    lines.extend(
        [
            "",
            "| Finding | Source | Status | URL | Destination / error |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for link in findings:
        detail = link.error or link.destination or "—"
        lines.append(
            f"| {escape_cell(link.category)} | {escape_cell(location(link))} | "
            f"{escape_cell(link.status)} | {escape_cell(link.url)} | {escape_cell(detail)} |"
        )
    return "\n".join(lines)


def render_text(result: AuditResult) -> str:
    counts = summary(result)
    lines = [
        (
            f"Scanned {counts['files']} file(s), {counts['links']} unique link(s): "
            f"{counts['HEALTHY']} healthy, "
            f"{counts['REDIRECT'] + counts['REDIRECT-CROSS-HOST']} redirect(s), "
            f"{counts['BROKEN']} broken, {counts['BLOCKED']} blocked."
        )
    ]
    for link in result.links:
        detail = (
            f" {link.error}"
            if link.error
            else (f" -> {link.destination}" if link.redirected else "")
        )
        lines.append(f"[{link.category}] {location(link)} {link.url}{detail}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = audit_paths(
            args.paths,
            workers=args.workers,
            timeout=args.timeout,
            allow_private=args.allow_private,
        )
    except (OSError, ValueError) as error:
        print(f"oss-link-auditor: error: {error}", file=sys.stderr)
        return 2

    if args.json:
        print(render_json(result))
    elif args.markdown:
        print(render_markdown(result))
    else:
        print(render_text(result))
    return 1 if args.fail_on_broken and result.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
