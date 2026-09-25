"""Core Markdown link extraction and HTTP auditing."""

from __future__ import annotations

import concurrent.futures
import ipaddress
import re
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from dataclasses import dataclass, replace
from pathlib import Path

INLINE_LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*(https?://[^)\s]+)")
REFERENCE_LINK_RE = re.compile(r"^\s*\[[^\]]+\]:\s*<?(https?://[^>\s]+)>?", re.MULTILINE)
AUTOLINK_RE = re.compile(r"<(https?://[^>\s]+)>")


@dataclass(frozen=True)
class SourceLocation:
    path: str
    line: int


@dataclass(frozen=True)
class LinkResult:
    url: str
    status: int | None
    destination: str | None
    error: str | None = None
    sources: tuple[SourceLocation, ...] = ()

    @property
    def redirected(self) -> bool:
        return bool(self.destination and self.destination.rstrip("/") != self.url.rstrip("/"))

    @property
    def failed(self) -> bool:
        return self.error is not None or self.status is None or self.status >= 400

    @property
    def cross_host_redirect(self) -> bool:
        if not self.redirected or not self.destination:
            return False
        source = urllib.parse.urlsplit(self.url).hostname
        destination = urllib.parse.urlsplit(self.destination).hostname
        return source != destination

    @property
    def category(self) -> str:
        if self.error and self.error.startswith("BlockedTarget:"):
            return "BLOCKED"
        if self.failed:
            return "BROKEN"
        if self.cross_host_redirect:
            return "REDIRECT-CROSS-HOST"
        if self.redirected:
            return "REDIRECT"
        return "HEALTHY"


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


def extract_link_occurrences(markdown: str, path: Path) -> dict[str, set[SourceLocation]]:
    """Return URLs and their source lines for supported Markdown link forms."""
    occurrences: dict[str, set[SourceLocation]] = {}
    for pattern in (INLINE_LINK_RE, REFERENCE_LINK_RE, AUTOLINK_RE):
        for match in pattern.finditer(markdown):
            url = match.group(1)
            location = SourceLocation(str(path), markdown.count("\n", 0, match.start()) + 1)
            occurrences.setdefault(url, set()).add(location)
    return occurrences


def discover_markdown(paths: Iterable[Path]) -> list[Path]:
    """Expand files and directories into a deterministic Markdown file list."""
    discovered: set[Path] = set()
    for path in paths:
        if path.is_dir():
            discovered.update(
                candidate
                for candidate in path.rglob("*")
                if candidate.is_file() and candidate.suffix.lower() in {".md", ".markdown"}
            )
        elif path.is_file() and path.suffix.lower() in {".md", ".markdown"}:
            discovered.add(path)
    return sorted(discovered)


class BlockedTargetError(ValueError):
    """Raised when a URL resolves to a non-public network target."""


def validate_public_target(url: str) -> None:
    """Reject loopback, private, link-local, multicast, and reserved targets."""
    hostname = urllib.parse.urlsplit(url).hostname
    if not hostname:
        raise BlockedTargetError("URL has no hostname")

    try:
        addresses = {ipaddress.ip_address(hostname)}
    except ValueError:
        try:
            addresses = {
                ipaddress.ip_address(item[4][0])
                for item in socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
            }
        except socket.gaierror as error:
            raise OSError(f"DNS lookup failed: {error}") from error

    blocked = [address for address in addresses if not address.is_global]
    if blocked:
        rendered = ", ".join(str(address) for address in sorted(blocked, key=str))
        raise BlockedTargetError(f"non-public network address: {rendered}")


def describe_network_error(error: Exception) -> str:
    """Render common network failures as actionable, security-safe messages."""
    reason = getattr(error, "reason", None)
    if isinstance(error, ssl.SSLCertVerificationError) or isinstance(
        reason, ssl.SSLCertVerificationError
    ):
        return (
            "TLSCertificateError: certificate verification failed. Install or update "
            "the CA certificates for this Python environment; TLS verification was not disabled."
        )
    return f"{type(error).__name__}: {error}"


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Validate every redirect destination before urllib connects to it."""

    def __init__(self, *, allow_private: bool = False) -> None:
        self.allow_private = allow_private
        super().__init__()

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not self.allow_private:
            validate_public_target(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def check_link(url: str, timeout: float = 15.0, *, allow_private: bool = False) -> LinkResult:
    """Fetch one link using normal TLS verification and report its final URL."""
    if not allow_private:
        try:
            validate_public_target(url)
        except BlockedTargetError as error:
            return LinkResult(url, None, None, f"BlockedTarget: {error}")
        except OSError as error:
            return LinkResult(url, None, None, f"{type(error).__name__}: {error}")

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "OSSLinkAuditor/0.1 (+https://github.com/Aryalmilan-max/oss-link-auditor)"
            )
        },
        method="GET",
    )
    try:
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ssl.create_default_context()),
            SafeRedirectHandler(allow_private=allow_private),
        )
        with opener.open(request, timeout=timeout) as response:
            return LinkResult(url, response.status, response.geturl())
    except BlockedTargetError as error:
        return LinkResult(url, None, None, f"BlockedTarget: {error}")
    except urllib.error.HTTPError as error:
        return LinkResult(url, error.code, error.geturl(), str(error))
    # Third-party HTTP handlers can raise non-stdlib exception types. Convert all
    # of them to review findings so one URL cannot abort the complete audit.
    except Exception as error:  # noqa: BLE001
        return LinkResult(url, None, None, describe_network_error(error))


def audit_paths(
    paths: Iterable[Path],
    *,
    workers: int = 12,
    timeout: float = 15.0,
    allow_private: bool = False,
) -> AuditResult:
    """Audit unique links found in Markdown files beneath the supplied paths."""
    if workers < 1:
        raise ValueError("workers must be at least 1")
    if timeout <= 0:
        raise ValueError("timeout must be greater than 0")
    files = discover_markdown(paths)
    if not files:
        raise ValueError("No Markdown files found in the supplied paths.")

    occurrences: dict[str, set[SourceLocation]] = {}
    for path in files:
        for url, locations in extract_link_occurrences(
            path.read_text(encoding="utf-8"), path
        ).items():
            occurrences.setdefault(url, set()).update(locations)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        checked = pool.map(
            lambda url: check_link(url, timeout, allow_private=allow_private),
            sorted(occurrences),
        )
        links = tuple(
            replace(
                link,
                sources=tuple(
                    sorted(occurrences[link.url], key=lambda item: (item.path, item.line))
                ),
            )
            for link in checked
        )

    return AuditResult(tuple(str(path) for path in files), links)
