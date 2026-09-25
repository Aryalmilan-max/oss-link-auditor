# Security policy

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature if it is enabled for
the repository. Otherwise, contact the maintainer privately rather than opening
a public issue containing exploit details.

## Security boundaries

The tool makes outbound GET requests to links supplied by repository content.
By default it resolves each target before connecting and blocks loopback,
private, link-local, multicast, and reserved addresses. Redirect destinations
receive the same check. Normal TLS certificate verification remains enabled.

DNS can change between validation and connection. This protection reduces risk
but does not replace network isolation. Do not run link checks from untrusted
pull requests on self-hosted runners that can reach internal services. The
`--allow-private` option is intended only for trusted internal documentation
and the deterministic local demo.
