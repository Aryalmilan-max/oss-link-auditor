# URL exclusion syntax proposal

Issue [#4](https://github.com/Aryalmilan-max/oss-link-auditor/issues/4)
requests repeatable URL exclusions with visible reasons. The proposed CLI syntax is:

```text
--exclude 'url:https://example.org/retired|Archived documentation'
--exclude 'host:*.example.org|Staging subdomains are not public'
```

- `url:` matches one complete URL exactly, including its path and query.
- `host:` matches one hostname exactly. A leading `*.` matches subdomains only.
- `|` separates the pattern from a required, non-empty human reason.
- Repeat `--exclude` for more rules. The first matching rule supplies the reason.
- Excluded public targets appear as `EXCLUDED` with the pattern and reason in text,
  Markdown, and JSON output. They are never counted as healthy or broken.
- Target safety checks run before exclusion. A private or loopback target remains
  `BLOCKED`, even if a rule matches it. DNS failures remain `BROKEN`.
- With no `--exclude` option, report fields and behavior stay as they are today.

Invalid prefixes, empty patterns or reasons, malformed URLs or hostnames, and
wildcards outside the leading `*.` host form produce CLI usage errors.
