# Chapter 2: Set Up the Project

[Home](../README.md) · **Chapter 2 of 11**

In this chapter you will fork the repository, create its local configuration,
and open the development container.

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
`OPENAI_*` placeholders unchanged until Chapter 9.

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

## Before You Continue

Open a new VS Code terminal and run:

```bash
pwd
```

It should print `/workspaces`.

If the container does not open, use the
[troubleshooting guide](reference/troubleshooting.md#development-container-will-not-open).

---

[← Previous: Prerequisites](01-prerequisites.md) ·
[Next: Run the API →](03-run-the-api.md)
