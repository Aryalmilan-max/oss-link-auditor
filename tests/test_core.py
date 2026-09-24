from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from oss_link_auditor.core import LinkResult, audit_paths, discover_markdown, extract_links


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


class DiscoverMarkdownTests(TestCase):
    def test_discovers_markdown_recursively(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "nested").mkdir()
            (root / "README.md").write_text("", encoding="utf-8")
            (root / "nested" / "guide.markdown").write_text("", encoding="utf-8")
            (root / "ignored.txt").write_text("", encoding="utf-8")
            self.assertEqual(len(discover_markdown([root])), 2)


class AuditPathsTests(TestCase):
    @patch("oss_link_auditor.core.check_link")
    def test_checks_each_unique_link_once(self, check_link_mock) -> None:
        check_link_mock.side_effect = lambda url, timeout: LinkResult(url, 200, url)
        with TemporaryDirectory() as directory:
            readme = Path(directory) / "README.md"
            readme.write_text(
                "[one](https://example.com) [two](https://example.com)", encoding="utf-8"
            )
            result = audit_paths([readme], workers=1)
        self.assertEqual(len(result.links), 1)
        check_link_mock.assert_called_once_with("https://example.com", 15.0)
