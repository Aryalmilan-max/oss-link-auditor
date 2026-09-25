"""Audit links in Markdown documents."""

from .core import AuditResult, LinkResult, SourceLocation, audit_paths, extract_links

__all__ = [
    "AuditResult",
    "LinkResult",
    "SourceLocation",
    "audit_paths",
    "extract_links",
]
__version__ = "0.1.1"
