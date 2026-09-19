# DevOps operations

## Workflow and ownership

The maintainer owns triage and merge/release authorization. Agents can implement
assigned issues through a validated PR. dev is the default integration branch;
main receives explicitly approved promotions. Do not squash dev into main; use a
merge commit and merge main back into dev afterward. No auto-merge is enabled.

The dedicated [project](https://github.com/users/skotschi/projects/2) contains issues,
not duplicate PR cards. Status: Backlog, Ready, In progress, In review, Done.
Priority: P1 urgent, P2 normal (default), P3 optional. Type labels: bug, feature,
maintenance; blocked names a pending dependency. Configure native workflows to
add repository issues and move closed issues to Done; verify they are enabled
before relying on them. Agents set intermediate status and P2 on new issues,
and restore status when reopening an issue. Native automation does not
assign implementation authority. Declined/duplicate issues close with a reason.

## Required validation

The stable check name is `CI / gate`; require it only after verifying successful
runs and integrating the CI bootstrap PR so all subsequent PRs can produce it.
PR policy requires a real same-repository issue for task PRs to dev; promotion PRs to main must come from this repository's dev branch. Bots follow
the same issue policy. A PR author must not remove or weaken required validation.

Backend: install backend/requirements-dev.txt with hashes and run
`python -m pytest backend/tests -q` from the root. Frontend: in frontend, run
`npm ci`, `node --test tests/errors.test.mjs`, `npm run check`, `npm run lint`,
and `npm run build`. CI also validates
workflow syntax and its own policy/gate tests. Desktop/build changes and promotion
PRs build Windows NSIS and macOS ARM DMGs and smoke-test the bundled sidecar's
HTTP startup and stdin shutdown using temporary data. Artifact builds do not publish.
macOS Intel CI and release packaging are temporarily omitted at the maintainer's
request; issue #13 tracks its bundled OpenSSL startup failure and restoration.
Intel is deferred, not validated. Windows and macOS ARM remain required.

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
Build artifacts and checksums first. Dispatch `Release Build` with an existing
`vMAJOR.MINOR.PATCH` tag (optional prerelease suffix) on main. Leave `publish` false for artifact-only validation.
Publishing must be dispatched from main with `publish` true, only after explicit
authorization. The workflow resolves the tag to an immutable commit for validation,
checks it again before publication, and refuses to overwrite an existing release. No signing/notarization credentials are introduced by this setup.

## Verified activation

Live settings verified on 2026-09-19: dev is default; auto-merge is disabled;
main/dev require PRs and resolved conversations, including administrators, and
block force pushes/deletion. Independent approval count is zero. Workflow tokens
are read-only by default and cannot approve PRs. Private vulnerability reporting
is enabled. The dedicated project has the five statuses and P1/P2/P3 priorities.

Bootstrap PRs #9, #6, and #8 are integrated into dev. The
[bootstrap CI run](https://github.com/skotschi/ebon-reader/actions/runs/35439506003)
passed before the exact `CI / gate` check from GitHub Actions (app ID 15368) was
required on dev and main. The protection API confirms strict up-to-date checking
on both branches. Scheduled security scanning and Dependabot configuration are
now on the default branch; configuration presence is not evidence of a completed
scheduled run.

The maintainer enabled the native
[project workflows](https://github.com/users/skotschi/projects/2/workflows).
The API confirms Auto-add to project, Item added to project, and Item closed are
enabled; Auto-close issue remains disabled. The configured auto-add scope is
repository `skotschi/ebon-reader` with filter `is:issue is:open`, as requested in
the browser setup. The API exposes enabled states, not the saved filter, so the
filter itself was not independently read back.

[Synthetic verification issue #15](https://github.com/skotschi/ebon-reader/issues/15)
was automatically added with Backlog status and moved automatically to Done when
closed. No manual Status update was used. Priority was initially unset: P2 is a
workflow convention that agents must still apply explicitly, not a verified
native default. P2 was applied manually to the test issue after observing this.
Agents also set intermediate statuses and restore status when reopening issues.

Issue #5 records the setup and validation. No promotion, tag, or release was
performed during setup.

## References

- [GitHub secure workflow guidance](https://docs.github.com/en/actions/reference/security/secure-use)
- [Project native automation](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-built-in-automations)
- [Protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
