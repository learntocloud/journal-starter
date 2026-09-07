# Sync Your Fork with Upstream

[Home](../../README.md) · [Capstone](../01-prerequisites.md)

Use this guide when `learntocloud/journal-starter` has updates that are not in
your fork. Keep your existing fork so you preserve branches, pull requests, and
repository settings.

Run these commands from the project root inside the devcontainer.

## 1. Save Your Work

```bash
git status
git branch --show-current
```

Commit work you want to keep and make sure the working tree is clean. Note your
current feature branch, then create a backup pointer:

```bash
git branch backup/before-upstream-sync
```

Choose another name if that branch already exists.

## 2. Check the Remotes

`origin` must point to your fork. Add `upstream` once if it is missing:

```bash
git remote -v
git remote add upstream https://github.com/learntocloud/journal-starter.git
```

Do not run the second command if `upstream` already exists.

## 3. Create a Synchronization Branch

```bash
git checkout main &&
git pull --ff-only origin main &&
git fetch upstream &&
git checkout -b maintenance/sync-upstream &&
git merge upstream/main
```

This keeps your fork's `main` unchanged while you review the update.

## 4. Resolve Conflicts If Needed

Use `git status` to find conflicts. In each affected file, combine the upstream
changes with the task behavior you intend to keep, then remove the conflict
markers:

```text
<<<<<<< HEAD
your version
=======
upstream version
>>>>>>> upstream/main
```

Stage each resolved file and review the result:

```bash
git add path/to/resolved-file
git diff --cached
git commit -m "Merge upstream changes"
```

If there were no conflicts, Git normally creates the merge commit
automatically. Use `git merge --abort` to abandon an unresolved merge.

Do not blindly accept all incoming changes, reset committed work, or
force-push to bypass conflicts.

## 5. Test and Merge the Update

Run `uv sync`, then the checks appropriate for your latest completed chapter.
Push the branch:

```bash
git push -u origin maintenance/sync-upstream
```

Open a pull request to your fork's `main`. Use the label for your latest
completed task, or `task:setup` if you have not completed an exercise.

After merging:

```bash
git checkout main && git pull --ff-only origin main
```

If you still have a feature branch in progress:

```bash
git checkout your-feature-branch && git merge main
```

Keep the backup branch until you are satisfied that your work is preserved.
