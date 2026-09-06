# Sync Your Fork with Upstream

[README](../README.md) > Upstream synchronization

If the original `learntocloud/journal-starter` repository has changed, merge its
updates into your fork. **Do not delete your fork to update it.** Keeping it
preserves your branches, pull requests, discussions, and repository settings.

Run these commands from the **project root** in the VS Code terminal. Stop if a
command reports an error; do not continue with later steps until it is resolved.
In the command blocks, `&&` runs the next command only if the previous one succeeds.

## 1. Save your work before switching branches

```bash
git status
git branch --show-current
```

Note your current feature branch. Commit any intended changes there using the
[development workflow](workflow.md#4-commit-and-push), and make sure `git status`
reports a clean working tree. Do not commit `.env` or other secrets.
Create a backup pointer to the current commit:

```bash
git branch backup/before-upstream-sync
```

Choose a new backup name if that branch already exists. A backup branch
preserves committed work, not uncommitted files, ignored files, or database
contents. Keep your existing clone and database volume.

## 2. Verify your remotes

```bash
git remote -v
# origin    https://github.com/YOUR_USERNAME/journal-starter.git (fetch)
# origin    https://github.com/YOUR_USERNAME/journal-starter.git (push)
# upstream  https://github.com/learntocloud/journal-starter.git (fetch)
# upstream  https://github.com/learntocloud/journal-starter.git (push)
```

`origin` must point to **your fork**. If `upstream` is missing, add it once:

```bash
git remote add upstream https://github.com/learntocloud/journal-starter.git
```

If it already exists, verify its URL rather than adding it again.

## 3. Bring local main up to date with your fork

```bash
git checkout main && git pull --ff-only origin main
```

If Git refuses the fast-forward because local and remote `main` have diverged,
stop and reconcile those commits before continuing. Do not discard commits
or force-push to get past the error.

## 4. Merge upstream on a dedicated branch

```bash
git fetch upstream &&
git checkout -b maintenance/sync-upstream &&
git merge upstream/main
```

Choose a new branch name if `maintenance/sync-upstream` already exists, and
use that name in the later push command. This keeps your fork's `main`
unchanged while you review the update.

## 5. Resolve conflicts if Git reports them

Large upstream changes may conflict with your task implementations. Run
`git status` to find unresolved files, then inspect conflict markers:

```text
<<<<<<< HEAD
# your code
=======
# upstream code
>>>>>>> upstream/main
```

Combine the upstream changes with your intended behavior. Do not blindly
accept all incoming changes: that can remove your completed task code.
If the structure changed, adapt your implementation to it and refer to your
backup branch as needed.

After editing each conflict, remove the markers and stage the resolved files.
Replace `path/to/resolved-file` below with an actual filename; repeat the
`git add` command for each resolved file. Review the staged changes before
completing the merge:

```bash
git add path/to/resolved-file
git diff --cached
git commit -m "Merge upstream changes"
```

If there were no conflicts, Git normally completes the merge automatically,
so an extra commit is not needed. To abandon an unresolved merge and discard
your in-progress conflict resolutions, use `git merge --abort`.

## 6. Review the update and open a PR on your fork

Run `uv sync`, then the relevant tests and code-quality commands from the
[development workflow](workflow.md#3-run-the-acceptance-and-code-quality-checks).
Failures for unfinished learner tasks are still expected; investigate new
failures in work you have already completed.

Push the synchronization branch to **your fork**:

```bash
git push -u origin maintenance/sync-upstream
```

Open a PR from this branch to your fork's `main`, review it, and merge it.
Do not target `learntocloud/journal-starter`.

## 7. Refresh main and update any feature branch still in progress

After merging the PR:

```bash
git checkout main && git pull --ff-only origin main
```

If you have a feature branch to continue:

```bash
git checkout your-feature-branch &&
git merge main
```

Replace `your-feature-branch` with the branch you noted in step 1. Resolve any
conflicts using the same process, and keep the backup branch until you are
satisfied that your work is preserved.

This workflow uses merges so existing commit history is preserved; it does not
require deleting the fork, resetting branches, or force-pushing.

Return to the [task workflow](workflow.md#for-each-task). If the upstream update
changed the devcontainer configuration, also consult the
[restart and rebuild guidance](troubleshooting.md#restarting-versus-rebuilding).
