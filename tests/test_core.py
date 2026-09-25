from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch
from urllib.request import Request

from oss_link_auditor.core import (
    BlockedTargetError,
    LinkResult,
    SafeRedirectHandler,
    SourceLocation,
    audit_paths,
    discover_markdown,
    extract_link_occurrences,
    extract_links,
    validate_public_target,
)


class ExtractLinksTests(TestCase):
    def test_extracts_supported_markdown_forms_and_ignores_images(self) -> None:
        markdown = """
        [Inline](https://example.com/inline)
        ![Image](https://example.com/image.png)
        [reference]: https://example.com/reference
        <https://example.com/auto>
        """
        self.assertEqual(
            extract_links(markdown),
            {
                "https://example.com/inline",
                "https://example.com/reference",
                "https://example.com/auto",
            },
        )

    def test_deduplicates_links(self) -> None:
        self.assertEqual(
            extract_links("[one](https://example.com) [two](https://example.com)"),
            {"https://example.com"},
        )

    def test_records_exact_source_lines(self) -> None:
        occurrences = extract_link_occurrences(
            "title\n[one](https://example.com)\n\n<https://example.com>", Path("README.md")
        )
        self.assertEqual(
            occurrences["https://example.com"],
            {SourceLocation("README.md", 2), SourceLocation("README.md", 4)},
        )


class DiscoverMarkdownTests(TestCase):
    def test_discovers_markdown_recursively(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "nested").mkdir()
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "nested" / "guide.markdown").write_text("", encoding="utf-8")
            (root / "ignored.txt").write_text("", encoding="utf-8")
            self.assertEqual(len(discover_markdown([root])), 2)


class NetworkSafetyTests(TestCase):
    def test_rejects_private_literal(self) -> None:
        with self.assertRaises(BlockedTargetError):
            validate_public_target("http://127.0.0.1/admin")

    def test_accepts_public_literal(self) -> None:
        validate_public_target("https://8.8.8.8/")

    @patch("oss_link_auditor.core.socket.getaddrinfo")
    def test_rejects_hostname_if_any_answer_is_private(self, lookup) -> None:
        lookup.return_value = [
            (2, 1, 6, "", ("93.184.216.34", 0)),
            (2, 1, 6, "", ("10.0.0.5", 0)),
        ]
        with self.assertRaises(BlockedTargetError):
            validate_public_target("https://example.test")

    def test_rejects_redirect_to_private_target(self) -> None:
        handler = SafeRedirectHandler()
        with self.assertRaises(BlockedTargetError):
            handler.redirect_request(
                Request("https://example.com"), None, 302, "Found", {}, "http://127.0.0.1/"
            )


class LinkResultTests(TestCase):
    def test_categories(self) -> None:
        samples = [
            (LinkResult("https://a.test", 200, "https://a.test"), "HEALTHY"),
            (LinkResult("https://a.test/old", 200, "https://a.test/new"), "REDIRECT"),
            (LinkResult("https://a.test", 200, "https://b.test"), "REDIRECT-CROSS-HOST"),
            (LinkResult("https://a.test", 404, "https://a.test", "HTTP 404"), "BROKEN"),
            (LinkResult("http://127.0.0.1", None, None, "BlockedTarget: private"), "BLOCKED"),
        ]
        for result, category in samples:
            with self.subTest(category=category):
                self.assertEqual(result.category, category)


class AuditPathsTests(TestCase):
    @patch("oss_link_auditor.core.check_link")
    def test_checks_each_unique_link_once_and_attaches_sources(self, check_link_mock) -> None:
        check_link_mock.side_effect = lambda url, timeout, allow_private=False: LinkResult(
            url, 200, url
        )
        with TemporaryDirectory() as directory:
            readme = Path(directory) / "README.md"
            readme.write_text(
                "[one](https://example.com)\n[two](https://example.com)", encoding="utf-8"
            )
            result = audit_paths([readme], workers=1)
        self.assertEqual(len(result.links), 1)
        self.assertEqual([source.line for source in result.links[0].sources], [1, 2])
        check_link_mock.assert_called_once_with("https://example.com", 15.0, allow_private=False)

    def test_errors_when_no_markdown_exists(self) -> None:
        with (
            TemporaryDirectory() as directory,
            self.assertRaisesRegex(ValueError, "No Markdown"),
        ):
            audit_paths([Path(directory)])

    def test_validates_worker_and_timeout_values(self) -> None:
        with self.assertRaisesRegex(ValueError, "workers"):
            audit_paths([Path("README.md")], workers=0)
        with self.assertRaisesRegex(ValueError, "timeout"):
            audit_paths([Path("README.md")], timeout=0)
