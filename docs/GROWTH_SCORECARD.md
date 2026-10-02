# Adoption and growth scorecard

The long-term ambition is broad maintainer adoption and, if the project earns
it, 10,000 GitHub stars. Stars are a discovery signal, not evidence that the
tool is useful. This scorecard prevents a large vanity target from replacing
product and adoption work.

## Public baseline: 2026-10-02

Verified from public GitHub repository and Actions data:

- 0 stars, 0 forks, and 0 watchers
- public `v0.1.1` release and GitHub Marketplace listing
- Test and CodeQL workflows passing on the default branch
- one successful workflow run in a separate public consumer repository
- one open, bounded `good first issue`

GitHub traffic metrics require authenticated repository access and are not
backfilled or guessed here.

## Milestone gates

### 0 to 10 stars: prove setup and usefulness

- get two independent maintainers to run the Action or CLI
- record setup friction and one concrete maintenance decision from each test
- make the first-run path obvious from the top of the README
- ship only changes supported by reproducible feedback

### 10 to 100 stars: create contributor gravity

- maintain a response time for issues and pull requests that the maintainer can
  sustain
- publish one evidence-backed technical article or demo per meaningful release
- keep at least two genuinely bounded contributor tasks available
- publish verified adoption examples only with the relevant maintainer's consent

### 100 to 1,000 stars: expand integrations

- add outputs such as SARIF only when real users request them
- reduce installation friction without weakening security defaults
- maintain stable version tags and upgrade notes
- track public workflow adoption, external contributors, and returning users

### 1,000 to 10,000 stars: scale what already works

- invest only in channels and integrations with demonstrated conversion
- collaborate with documentation and awesome-list communities instead of mass
  outreach
- keep releases, security guidance, and maintainer support dependable
- treat 10,000 as an earned outcome, never a deadline or guarantee

## Guardrails

Never buy, trade, or automate stars; use bot accounts; ask unrelated people to
star the repository; mass-DM maintainers; or manufacture usage claims. Public
posts and direct outreach are reviewed by a human immediately before sending.

## Weekly review

Record the evidence in [LAUNCH_METRICS.md](LAUNCH_METRICS.md), then answer:

1. Which channel brought qualified maintainers?
2. How many people completed the demo or consumer workflow?
3. What setup problem repeated?
4. Which feedback changed the product or documentation?
5. What should stop, continue, or receive one more experiment?
