# Repository working rules

These rules apply to all work in this repository, including documentation,
dependency updates, automation, and fixes.

## Branches and releases

- Never commit directly to `main` or `dev`. Make changes and commits on a
  short-lived feature branch unless the user explicitly authorizes an exception
  for the current task. General instructions to implement, commit, or ship work
  do not constitute an exception.
- Start task branches from the current `dev` branch. Use descriptive names such
  as `feature/receipt-search`, `fix/import-total`, or `chore/update-dependencies`.
- Integrate task branches into `dev`, preferably through a pull request targeting
  `dev`. Do not target `main` with feature pull requests.
- Merge `dev` into `main` only when the user explicitly requests that promotion.
  Do not enable automatic promotion to `main`. A request to finish a feature or
  merge its pull request authorizes integration into `dev`, not release promotion.
- Before promotion, summarize the changes and validation results for the exact
  revision being promoted. Preserve shared history with a merge commit or
  fast-forward; do not squash the long-lived `dev` branch into `main`. If a merge
  commit is created on `main`, merge `main` back into `dev` afterward.
- Publishing a release, tag, or deployment requires authorization for that action;
  a merge into `main` alone is not authorization to publish.

## Git safety

- Inspect branch, remotes, working-tree changes, and the intended diff before
  editing, committing, pushing, or merging. Recheck the current branch immediately
  before a commit or merge.
- `origin` is `skotschi/ebon-reader`. `upstream` is `fmmix/ebon-reader` and is
  read-only for this workflow. Never push to upstream unless explicitly requested.
- Fetch before using remote branch state. Update local integration branches with
  fast-forward-only pulls; investigate divergence instead of resetting it away.
- Preserve unrelated user edits. Stage explicit paths or hunks, and review the
  staged diff. Keep commits focused on one purpose.
- Never force-push, rewrite shared history, discard changes, or delete unmerged
  branches without explicit authorization. Do not bypass failing hooks or checks.
- Bring upstream changes into a task branch for review and testing, then integrate
  into `dev`. Do not sync upstream directly into `main`.

## Validation and data

- Run checks appropriate to the change before integration. Report failures,
  skipped checks, and environment limitations accurately; do not claim unrun
  checks passed.
- For backend behavior changes, run `python -m pytest backend/tests -q` from the
  repository root using the backend environment. Add focused regression coverage
  for bug fixes when useful.
- For frontend behavior or dependency changes, run `npm run check`, `npm run lint`,
  and `npm run build` in `frontend`, plus a relevant UI smoke test when possible.
- For desktop/runtime changes, verify the affected Tauri build and backend
  startup/shutdown on the available platform; state which platforms were tested.
- Keep dependency updates small. Separate major migrations from routine updates,
  review compatibility and security advisories, and include changed lockfiles.
  Audit frontend build dependencies as well as runtime dependencies.
- Use temporary databases and synthetic receipts for tests. Never reset, migrate,
  or overwrite a user's real receipt database as part of a test. Back up real data
  before an authorized migration.
- Never commit secrets, personal receipts, local databases, or logs containing
  personal data. Review added files for these before committing.

## Enforcement and review

- Prefer small pull requests explaining the problem, final behavior, validation,
  and any migration or data impact. Resolve review comments before merging.
- These instructions guide agents; they are not server-side access controls.
  Recommended GitHub protection for `main` and `dev`: require pull requests,
  passing CI checks, resolved review conversations, and block force pushes and
  deletion. Require independent approval when another reviewer is available.
- Do not claim branch protections or CI checks are active without verifying the
  repository settings and workflow runs. Add required check names only after
  those checks actually exist and run on the relevant pull requests.

## Sources

- [GitHub: protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Atlassian: feature branch workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/feature-branch-workflow/)
- [Atlassian: Gitflow workflow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow/)

This repository uses a lightweight feature → dev → main workflow chosen by the
user; full Gitflow release and hotfix branch conventions are not required.
