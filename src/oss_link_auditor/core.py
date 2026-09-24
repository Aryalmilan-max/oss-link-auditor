"""Core Markdown link extraction and HTTP auditing."""

from __future__ import annotations

import concurrent.futures
import re
import ssl
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INLINE_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(https?://[^)\s]+)")
REFERENCE_LINK_RE = re.compile(
    r"^\s*\[[^\]]+\]:\s*<?(https?://[^>\s]+)>?", re.MULTILINE
)
AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")


@dataclass(frozen=True)
class LinkResult:
    url: str
    status: int | None
    destination: str | None
    error: str | None = None

    @property
    def redirected(self) -> bool:
        return bool(
            self.destination
            and self.destination.rstrip("/") != self.url.rstrip("/")
        )

    @property
    def failed(self) -> bool:
        return self.error is not None or self.status is None or self.status >= 400


@dataclass(frozen=True)
class AuditResult:
    files: tuple[str, ...]
    links: tuple[LinkResult, ...]

    @property
    def failures(self) -> tuple[LinkResult, ...]:
        return tuple(link for link in self.links if link.failed)

    @property
    def redirects(self) -> tuple[LinkResult, ...]:
        return tuple(link for link in self.links if link.redirected and not link.failed)


def extract_links(markdown: str) -> set[str]:
    """Return unique HTTP(S) links from common Markdown link forms."""
    return {
        *INLINE_LINK_RE.findall(markdown),
        *REFERENCE_LINK_RE.findall(markdown),
        *AUTOLINK_RE.findall(markdown),
    }


def discover_markdown(paths: Iterable[Path]) -> list[Path]:
    """Expand files and directories into a deterministic Markdown file list."""
    discovered: set[Path] = set()
    for path in paths:
        if path.is_dir():
            discovered.update(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file()
                and candidate.suffix.lower() in {".md", ".markdown"}
            )
        elif path.is_file() and path.suffix.lower() in {".md", ".markdown"}:
            discovered.add(path)
    return sorted(discovered)


def check_link(url: str, timeout: float = 15.0) -> LinkResult:
    """Fetch one link using normal TLS verification and report its final URL."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "OSSLinkAuditor/0.1 (+https://github.com/)"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(
            request, timeout=timeout, context=ssl.create_default_context()
        ) as response:
            return LinkResult(url, response.status, response.geturl())
    except urllib.error.HTTPError as error:
        return LinkResult(url, error.code, error.geturl(), str(error))
    except Exception as error:  # Network errors require review, never silent deletion.
        return LinkResult(url, None, None, f"{type(error).__name__}: {error}")


def audit_paths(
    paths: Iterable[Path], *, workers: int = 12, timeout: float = 15.0
) -> AuditResult:
    """Audit unique links found in Markdown files beneath the supplied paths."""
    files = discover_markdown(paths)
    urls: set[str] = set()
    for path in files:
        urls.update(extract_links(path.read_text(encoding="utf-8")))

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        links = tuple(pool.map(lambda url: check_link(url, timeout), sorted(urls)))

    return AuditResult(tuple(str(path) for path in files), links)
