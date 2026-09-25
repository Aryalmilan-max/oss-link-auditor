# Roadmap

The roadmap is intentionally small and evidence-driven.

## Near term

- configurable URL exclusions with documented reasons
- retry policy for transient failures
- optional report files for CI artifacts
- line-number and source-file context for each link
- tests for more Markdown edge cases

## Later, if maintainers need it

- rate limits per host
- pluggable status policies
- SARIF or GitHub job-summary output
- stable tagged releases and package distribution

## Out of scope

- automatic deletion of failed links
- bypassing TLS certificate verification
- treating one failed request as proof that a resource is permanently gone
- undisclosed telemetry
