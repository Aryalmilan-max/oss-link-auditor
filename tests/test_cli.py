import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from unittest import TestCase
from unittest.mock import patch

from oss_link_auditor.cli import main, render_markdown, render_text
from oss_link_auditor.core import AuditResult, LinkResult, SourceLocation

SAMPLE = AuditResult(
    ("README.md",),
    (
        LinkResult(
            "https://good.test", 200, "https://good.test", sources=(SourceLocation("README.md", 2),)
        ),
        LinkResult(
            "https://old.test", 200, "https://new.test", sources=(SourceLocation("README.md", 4),)
        ),
        LinkResult(
            "https://bad.test",
            404,
            "https://bad.test",
            "HTTP Error 404",
            (SourceLocation("README.md", 6),),
        ),
    ),
)


class CliTests(TestCase):
    @patch("oss_link_auditor.cli.audit_paths", return_value=SAMPLE)
    def test_json_output_is_structured(self, audit_mock) -> None:
        output = StringIO()
        with redirect_stdout(output):
            code = main([".", "--json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(payload["summary"]["links"], 3)
        self.assertEqual(payload["links"][1]["category"], "REDIRECT-CROSS-HOST")

    @patch("oss_link_auditor.cli.audit_paths", return_value=SAMPLE)
    def test_fail_on_broken_returns_one(self, audit_mock) -> None:
        with redirect_stdout(StringIO()):
            self.assertEqual(main([".", "--fail-on-broken"]), 1)

    @patch("oss_link_auditor.cli.audit_paths", side_effect=ValueError("No Markdown files found"))
    def test_actionable_error_returns_two(self, audit_mock) -> None:
        error = StringIO()
        with redirect_stderr(error):
            code = main(["missing"])
        self.assertEqual(code, 2)
        self.assertIn("No Markdown files found", error.getvalue())

    def test_markdown_report_surfaces_location_and_redirect(self) -> None:
        report = render_markdown(SAMPLE)
        self.assertIn("README.md:4", report)
        self.assertIn("REDIRECT-CROSS-HOST", report)

    def test_text_report_separates_url_from_error(self) -> None:
        report = render_text(SAMPLE)
        self.assertIn("https://bad.test HTTP Error 404", report)
