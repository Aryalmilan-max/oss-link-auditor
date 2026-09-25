# Launch content

These are drafts, not published claims. Replace bracketed fields only with
verified values and re-check each community's current rules before posting.

## Show HN

**Title:** Show HN: A source-aware link auditor that makes redirects visible

I maintain Markdown resource lists where a redirect is not automatically good
news: sometimes a project moved, and sometimes an expired domain now leads
somewhere unrelated.

I built OSS Link Auditor, a dependency-free Python CLI and GitHub Action. Its
trust report separates broken links, same-host redirects, cross-host redirects,
and targets blocked by its public-network policy. Every finding includes the
Markdown file and line. It never rewrites or deletes content automatically.

The repository includes a deterministic local demo (`make demo`) and 3.10-3.13
CI. I would value edge cases from maintainers of docs and resource catalogs:
https://github.com/Aryalmilan-max/oss-link-auditor

## LinkedIn

Broken links are obvious. Successful redirects can be harder.

OSS Link Auditor is an open-source CLI and GitHub Action that turns broken
links, same-host redirects, cross-host redirects, and blocked network targets
into a report with exact Markdown source lines. It keeps TLS verification on,
has no runtime dependencies, and leaves every content decision to a human.

I am looking for maintainers who will test it on real documentation and share
edge cases—not just star it.

https://github.com/Aryalmilan-max/oss-link-auditor

## Short post

I built a dependency-free Markdown link auditor for maintainers. Its unusual
choice: a redirect is visible, and a cross-host redirect is a separate review
signal. Reports point to the exact file and line; private targets are blocked by
default. Deterministic demo: `make demo`.

https://github.com/Aryalmilan-max/oss-link-auditor

## One-to-one maintainer note

Hi [name] — I maintain Markdown resource lists and built a small link auditor
that reports cross-host redirects separately and points to exact source lines.
Your [repo/docs] looks like a relevant real-world test. If useful, I can help
you try it; no need to star or promote it. Repo: [URL]

Send only after confirming relevance. One message per person, no automated
follow-ups, and stop immediately if they decline or do not respond.

## GitHub release

**Hook:** Source-aware link auditing for Markdown is ready in v0.1.0.

**Context/value:** The release separates same-host redirects, cross-host
redirects, broken links, and blocked private targets, then points to every
source line. It ships as a dependency-free CLI and reusable Action.

**Demo/technical detail:** Run `make demo`; CI covers Python 3.10-3.13. Read the
security note before using self-hosted runners.

**CTA:** Try it on a real Markdown repository and report the first edge case.

## Reddit

**Proposed title:** I made a small Markdown link auditor that treats cross-host redirects as review signals

**Draft:** I maintain resource lists and wanted more context than pass/fail.
This dependency-free Python tool reports exact source lines and distinguishes a
same-host move from a cross-host redirect. It also blocks private-network
targets by default. The repository has a deterministic local demo, so you can
judge the output without trusting a hosted service. I would appreciate parser
or CI edge cases from maintainers: [repository URL]

Post only to a directly relevant subreddit after checking its current project
and self-promotion rules. Do not cross-post simultaneously.

## X

Broken link: obvious. Cross-host redirect: worth a look.

OSS Link Auditor gives Markdown maintainers a source-aware trust report—exact
file/line, safe network defaults, JSON/Markdown output, zero runtime deps.

Try `make demo` and tell me what breaks: [repository URL]

## Dev.to

**Title:** Why a successful redirect is still a documentation maintenance signal

**Outline:**

1. The failure mode: status-only checks hide destination changes.
2. The model: healthy, same-host redirect, cross-host redirect, broken, blocked.
3. The implementation: extraction index, unique queue, target validation.
4. The security boundary: why DNS checks do not replace network isolation.
5. Reproduce it with `make demo`, then audit a real repository.

End with the code and an invitation to submit a reproducible edge case.

## Hashnode

**Title:** Building a dependency-free, source-aware Markdown trust report

Focus on the architecture diagram, result data model, redirect validation, and
the design choice to keep content decisions human. Include a JSON output sample
and link to the exact release tag. CTA: integrate the Action and report setup
friction.

## Discord or Slack

Use only in a channel that explicitly permits project sharing:

> I built a small open-source Markdown link auditor after encountering resource
> lists where a successful redirect hid a changed destination. It reports exact
> source lines and separates cross-host redirects from ordinary moves. There is
> a deterministic local demo (`make demo`). If anyone maintains Markdown-heavy
> docs, I would value one real integration test: [repository URL]

One post, no @everyone, no unsolicited private follow-up.

## Twenty evidence-based content angles

1. Why a successful redirect remains a maintenance signal.
2. How source-line indexing reduces link-cleanup time.
3. Designing a link checker that never rewrites content.
4. The security boundary of auditing URLs from repository content.
5. DNS rebinding: what application checks can and cannot prevent.
6. Building useful CLI output for both humans and automation.
7. Why the project has zero runtime dependencies.
8. A walkthrough of the five trust categories.
9. Turning a CLI report into a GitHub Step Summary.
10. Testing HTTP behavior without depending on the public internet.
11. A contributor's guide to adding a Markdown parser edge case.
12. Why duplicate URLs should be checked once but retain every source.
13. Failure story: the missing-path command that silently succeeded, and its fix.
14. Error design: exit 0, 1, and 2 as distinct operational outcomes.
15. What belongs in v0.1.0—and what deliberately does not.
16. Comparing manual checks, status-only checks, and trust reports.
17. How to pin a reusable GitHub Action safely.
18. Measuring CLI startup without publishing meaningless benchmarks.
19. A transparent launch-week metrics review.
20. The next feature selected from real maintainer feedback.
