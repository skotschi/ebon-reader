# Contributing

Start with a [GitHub issue](https://github.com/skotschi/ebon-reader/issues/new/choose).
Describe the problem, intended outcome, acceptance criteria, and validation.
Use synthetic examples; never attach personal receipts, databases, or secrets.
For suspected vulnerabilities, use GitHub private vulnerability reporting instead.

Work is tracked in the [eBon Reader project](https://github.com/users/skotschi/projects/2).
New issues start in Backlog with priority P2. Triage makes them Ready; explicit
assignment starts work. Set In progress during implementation, In review when a
validated PR is ready, and Done after integration into dev. Use the blocked label
and name the dependency when progress needs a decision or another change.

Fetch origin and create a short-lived branch from current dev, named
`feature/42-receipt-search`, `fix/42-import-total`, or `chore/42-update-tooling`.
Preserve unrelated edits by using an isolated worktree when needed. Follow
[AGENTS.md](AGENTS.md) for Git safety, validation, and agent authority.

Open a small PR targeting dev. Include `Closes #42` for a completed issue or
`Refs #42` for partial work, explain the final behavior, and report validation and
data impact. The maintainer explicitly authorizes merging after checks pass and
review conversations are resolved. Agents may prepare and update PRs; assignment
does not authorize a merge. Automated dependency PRs need an issue before merge.

Integration into dev closes completed issues; it does not release the change.
Promotion from dev to main and publishing a release require separate instructions.
See [DevOps operations](docs/devops.md) for validation and rollout details.
