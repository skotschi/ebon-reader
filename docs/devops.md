# DevOps operations

## Workflow and ownership

The maintainer owns triage and merge/release authorization. Agents can implement
assigned issues through a validated PR. dev is the default integration branch;
main receives explicitly approved promotions. Do not squash dev into main; use a
merge commit and merge main back into dev afterward. No auto-merge is enabled.

The dedicated [project](https://github.com/users/skotschi/projects/2) contains issues,
not duplicate PR cards. Status: Backlog, Ready, In progress, In review, Done.
Priority: P1 urgent, P2 normal (default), P3 optional. Type labels: bug, feature,
maintenance; blocked names a pending dependency. Native workflows add repository
issues and move closed issues to Done. Agents set intermediate status and P2 on
new issues, and restore status when reopening an issue. Native automation does not
assign implementation authority. Declined/duplicate issues close with a reason.

## Required validation

The planned stable required check is `CI / gate`; activate it only after verifying
successful runs. PR policy requires a real same-repository issue for task PRs to
dev; promotion PRs to main must come from this repository's dev branch. Bots follow
the same issue policy. A PR author must not remove or weaken required validation.

Backend: install backend/requirements-dev.txt with hashes and run
`python -m pytest backend/tests -q` from the root. Frontend: in frontend, run
`npm ci`, `npm run check`, `npm run lint`, and `npm run build`. CI also validates
workflow syntax and its own policy/gate tests. Desktop/build changes and promotion
PRs build Windows NSIS and macOS ARM/Intel DMGs and smoke-test the bundled sidecar's
HTTP startup and stdin shutdown using temporary data. Artifact builds do not publish.

Security scans cover Python, Cargo, npm (including dev dependencies), and secrets
on PRs and weekly. npm high/critical findings and any Python/Cargo advisory block
validation. Any future exception needs an advisory-specific reason, owner, expiry,
and issue; no blanket ignores. Weekly Dependabot PRs target dev with major updates
kept separate. Review advisories and regenerate Python locks with the documented
locking workflow before merge. Scheduled failures are visible in Actions and must
be triaged into an issue by the maintainer; they do not authorize unattended fixes.

## Repository controls and bootstrap

Protect dev and main with PRs, strict required checks, resolved conversations, no
force pushes, and no deletion. Use zero required independent approvals for the
solo-maintainer baseline. Apply protections to administrators as well. Do not
require linear history, which conflicts with dev → main merge commits. Restrict
Actions tokens to read-only by default and disallow workflow-created approvals.

Bootstrap sequence: deliver documentation and CI through PRs; verify successful
check names; then require those checks. Never invent a required check that has not
run. A setting described here is desired configuration, not proof it is active.
Track verified settings and remaining activation in issue #5. If CI is not yet on
a protected branch, do not enable its required check until its setup PR has run.
Any known baseline failure must be fixed or explicitly tracked; do not bypass it.

## Controlled releases

Publishing requires explicit authorization separate from promotion. Release
validation must cover the exact tag revision and confirm it belongs to main.
Build artifacts and checksums first. Manual artifact builds never publish. The
release workflow should publish only when explicitly dispatched with publication
selected, after all validation/builds succeed. Do not replace existing release
assets implicitly. No signing/notarization credentials are introduced by this setup.

## References

- [GitHub secure workflow guidance](https://docs.github.com/en/actions/reference/security/secure-use)
- [Project native automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations)
- [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
