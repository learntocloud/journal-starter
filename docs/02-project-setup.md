# Chapter 2: Set Up the Project

[Home](../README.md) · **Chapter 2 of 10**

In this chapter you will fork the repository, create its local configuration,
and open the development container. Then add a cloud CLI in your first pull
request.

## 1. Fork and Clone

On GitHub, fork `learntocloud/journal-starter` to your account. Then run these
commands on your **host machine**, replacing `YOUR_USERNAME`:

```bash
git clone https://github.com/YOUR_USERNAME/journal-starter.git &&
cd journal-starter &&
git remote -v
```

`origin` should point to `YOUR_USERNAME/journal-starter`.

> Work in your own fork. Pull requests in this capstone must target your fork's
> `main` branch, not `learntocloud/journal-starter`.

Open the repository in VS Code:

```bash
code .
```

On your fork's **Actions** tab, enable workflows if GitHub prompts you to do so.

## 2. Create the Environment File

From the project root on your host machine:

```bash
cp .env-sample .env
```

The sample values are ready for the local databases and Tasks 1-3. Leave the
`OPENAI_*` placeholders unchanged until [Chapter 8](08-ai-setup.md).

The `.env` file is ignored by Git. Never commit it or copy credentials into the
GitHub Actions workflow.

## 3. Open the Development Container

In VS Code, select **Reopen in Container**. If it is not shown, open the Command
Palette with `Cmd/Ctrl + Shift + P` and choose
**Dev Containers: Reopen in Container**.

Wait for both containers to start:

- The development container provides Python and uv.
- The PostgreSQL container provides separate application and test databases.

Your database is stored in a named Docker volume, so rebuilding the
development container preserves your entries.

Open a new VS Code terminal and run:

```bash
pwd
```

It should print `/workspaces`.

If the container does not open, use the
[troubleshooting guide](reference/troubleshooting.md#development-container-will-not-open).

## 4. Add a Cloud CLI in Your First Pull Request

Use this small configuration change to practice making a branch and merging
a pull request before the Python exercises. Run these commands from the
**project root inside the devcontainer**.

Check that your working tree is clean with `git status`, then create a branch:

```bash
git status
git checkout main &&
git pull --ff-only origin main &&
git checkout -b setup/cloud-cli
```

Uncomment exactly one cloud CLI feature in
[`.devcontainer/devcontainer.json`](../.devcontainer/devcontainer.json).
Choose **Dev Containers: Rebuild Container** in VS Code, then open a new
terminal and run the command for your chosen CLI:

```bash
az --version
# or: aws --version
# or: gcloud --version
```

No cloud login or deployment is required.

Review the change, then commit and push only the configuration file:

```bash
git diff
git add .devcontainer/devcontainer.json
git commit -m "Add a cloud CLI to the devcontainer"
git push -u origin setup/cloud-cli
```

Never commit `.env` or other secrets.

1. Open a pull request to **your fork's `main` branch**, not
   `learntocloud/journal-starter`.
2. Add exactly one task label: `task:setup`. Create the label in your fork if
   it does not exist.
3. Wait for CI, review the diff, and merge the pull request.

The setup label runs starter checks without requiring unfinished exercises
to pass. See [Testing and CI](reference/testing-and-ci.md) for how labels
select tests.

## Before You Continue

After merging your pull request, return to the updated `main` branch:

```bash
git checkout main &&
git pull --ff-only origin main
```

You should now have a running devcontainer with one cloud CLI installed and
your setup pull request merged into your fork.

---

[← Previous: Prerequisites](01-prerequisites.md) ·
[Next: Run the API →](03-run-the-api.md)
