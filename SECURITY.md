# Security policy

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting feature if it is enabled for
the repository. Otherwise, contact the maintainer privately rather than opening
a public issue containing exploit details.

## Security boundaries

The tool makes outbound GET requests to links supplied by repository content.
Run it only against trusted repositories and in an environment with appropriate
network controls. TLS certificate verification remains enabled by design.
