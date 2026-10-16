import json
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from oss_link_auditor.cli import main, render_json, render_markdown, render_text
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

    def test_default_json_contract_has_no_exclusion_fields(self) -> None:
        payload = json.loads(render_json(SAMPLE))
        self.assertNotIn("EXCLUDED", payload["summary"])
        self.assertNotIn("exclusion", payload["links"][0])

    def test_exclusion_reason_appears_in_each_report(self) -> None:
        excluded = AuditResult(
            ("README.md",),
            (
                LinkResult(
                    "https://docs.example.org/old",
                    None,
                    None,
                    sources=(SourceLocation("README.md", 3),),
                    exclusion_pattern="host:*.example.org",
                    exclusion_reason="Staging only",
                ),
            ),
        )
        self.assertIn("EXCLUDED", render_text(excluded))
        self.assertIn("Staging only", render_text(excluded))
        self.assertIn("Staging only", render_markdown(excluded))
        payload = json.loads(render_json(excluded))
        self.assertEqual(payload["summary"]["EXCLUDED"], 1)
        self.assertEqual(payload["links"][0]["exclusion"]["reason"], "Staging only")

    @patch("oss_link_auditor.cli.audit_paths", return_value=SAMPLE)
    def test_repeatable_exclude_reaches_audit(self, audit_mock) -> None:
        with redirect_stdout(StringIO()):
            main(
                [
                    ".",
                    "--exclude",
                    "url:https://example.org/old|Archived",
                    "--exclude",
                    "host:*.example.org|Staging",
                ]
            )
        self.assertEqual(len(audit_mock.call_args.kwargs["exclusions"]), 2)

    def test_invalid_exclusion_is_cli_usage_error(self) -> None:
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as raised:
            main([".", "--exclude", "host:bad..org|Reason"])
        self.assertEqual(raised.exception.code, 2)

    @patch("oss_link_auditor.cli.audit_paths", return_value=SAMPLE)
    def test_retry_count_reaches_audit(self, audit_mock) -> None:
        with redirect_stdout(StringIO()):
            main([".", "--retries", "2"])
        self.assertEqual(audit_mock.call_args.kwargs["retries"], 2)

    def test_invalid_retry_count_is_cli_usage_error(self) -> None:
        for value in ("-1", "4", "many"):
            with self.subTest(value=value), redirect_stderr(StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    main([".", "--retries", value])
                self.assertEqual(raised.exception.code, 2)

    def test_fail_on_broken_keeps_excluded_and_blocked_distinct(self) -> None:
        with TemporaryDirectory() as directory:
            readme = Path(directory) / "README.md"
            readme.write_text("[public](https://8.8.8.8/check)", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main(
                    [
                        str(readme),
                        "--exclude",
                        "url:https://8.8.8.8/check|Known fixture",
                        "--fail-on-broken",
                        "--json",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertEqual(json.loads(output.getvalue())["links"][0]["category"], "EXCLUDED")

            readme.write_text("[private](http://127.0.0.1/admin)", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main(
                    [
                        str(readme),
                        "--exclude",
                        "url:http://127.0.0.1/admin|Known fixture",
                        "--fail-on-broken",
                        "--json",
                    ]
                )
            self.assertEqual(code, 1)
            self.assertEqual(json.loads(output.getvalue())["links"][0]["category"], "BLOCKED")
