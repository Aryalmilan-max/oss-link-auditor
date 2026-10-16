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
HOST_LABEL_RE = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?")


@dataclass(frozen=True)
class SourceLocation:
    path: str
    line: int


@dataclass(frozen=True)
class ExclusionRule:
    kind: str
    pattern: str
    reason: str

    @property
    def label(self) -> str:
        return f"{self.kind}:{self.pattern}"

    def matches(self, url: str) -> bool:
        if self.kind == "url":
            return url == self.pattern
        hostname = urllib.parse.urlsplit(url).hostname
        if not hostname:
            return False
        hostname = hostname.rstrip(".").lower()
        if self.pattern.startswith("*."):
            suffix = self.pattern[1:]
            return hostname.endswith(suffix) and hostname != self.pattern[2:]
        return hostname == self.pattern


def parse_exclusion_rule(value: str) -> ExclusionRule:
    """Parse an explicit URL or host pattern with a required review reason."""
    if "|" not in value:
        raise ValueError("expected PATTERN|REASON (for example, host:*.example.org|Staging)")
    expression, reason = (part.strip() for part in value.split("|", 1))
    if not reason:
        raise ValueError("exclusion reason must not be empty")
    kind, separator, pattern = expression.partition(":")
    if not separator or kind not in {"url", "host"} or not pattern:
        raise ValueError("exclusion pattern must start with url: or host:")
    if kind == "url":
        try:
            parsed = urllib.parse.urlsplit(pattern)
            port = parsed.port
            valid = (
                parsed.scheme in {"http", "https"}
                and bool(parsed.hostname)
                and (port is None or port > 0)
            )
        except ValueError as error:
            raise ValueError(f"invalid exclusion URL: {error}") from error
        if not valid or any(char.isspace() for char in pattern):
            raise ValueError("exclusion URL must be a complete HTTP(S) URL")
    else:
        pattern = pattern.lower().rstrip(".")
        hostname = pattern.removeprefix("*.")
        if not hostname or any(not HOST_LABEL_RE.fullmatch(label) for label in hostname.split(".")):
            raise ValueError("invalid exclusion host pattern")
        if "*" in hostname:
            raise ValueError("only a leading *. wildcard is supported for hosts")
    return ExclusionRule(kind, pattern, reason)


@dataclass(frozen=True)
class LinkResult:
    url: str
    status: int | None
    destination: str | None
    error: str | None = None
    sources: tuple[SourceLocation, ...] = ()
    exclusion_pattern: str | None = None
    exclusion_reason: str | None = None

    @property
    def redirected(self) -> bool:
        return bool(self.destination and self.destination.rstrip("/") != self.url.rstrip("/"))

    @property
    def failed(self) -> bool:
        if self.exclusion_reason is not None:
            return False
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
        if self.exclusion_reason is not None:
            return "EXCLUDED"
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


def exclude_link(url: str, rule: ExclusionRule, *, allow_private: bool = False) -> LinkResult:
    """Show an exclusion only after applying the usual target safety check."""
    if not allow_private:
        try:
            validate_public_target(url)
        except BlockedTargetError as error:
            return LinkResult(url, None, None, f"BlockedTarget: {error}")
        except OSError as error:
            return LinkResult(url, None, None, describe_network_error(error))
    return LinkResult(url, None, None, exclusion_pattern=rule.label, exclusion_reason=rule.reason)


def audit_paths(
    paths: Iterable[Path],
    *,
    workers: int = 12,
    timeout: float = 15.0,
    allow_private: bool = False,
    exclusions: Iterable[ExclusionRule] = (),
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

    rules = tuple(exclusions)

    def check_url(url: str) -> LinkResult:
        rule = next((item for item in rules if item.matches(url)), None)
        if rule is not None:
            return exclude_link(url, rule, allow_private=allow_private)
        return check_link(url, timeout, allow_private=allow_private)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as pool:
        checked = pool.map(check_url, sorted(occurrences))
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
