"""Audit links in Markdown documents."""

from .core import AuditResult, LinkResult, audit_paths, extract_links

__all__ = ["AuditResult", "LinkResult", "audit_paths", "extract_links"]
__version__ = "0.1.0"
