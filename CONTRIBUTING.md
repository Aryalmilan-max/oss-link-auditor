# Contributing

Thank you for helping improve OSS Link Auditor.

1. Open an issue for behavior changes that affect reports or exit codes.
2. Keep pull requests focused and include tests for new parsing or reporting behavior.
3. Do not disable TLS verification to make a failing site pass.
4. Do not add automatic link deletion. Network failures require human review.
5. Run `python -m unittest discover -s tests -v` before submitting a change.

Good first issues include parser edge cases, documentation improvements, and
tests that reproduce a real maintainer workflow. Larger features should begin
with an issue so their command-line and reporting behavior can be agreed first.

Please use factual commit and pull-request descriptions and disclose any relevant
affiliation when proposing behavior tailored to a particular service.
