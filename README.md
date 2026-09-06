# Topic 5: Capstone - Journal API

[![CI](https://github.com/learntocloud/journal-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/learntocloud/journal-starter/actions/workflows/ci.yml)

Build your Python skills by completing a **FastAPI + PostgreSQL** application
that helps people track their daily learning journey.

By the end of this capstone, your API should work locally and be ready for the
next phase's cloud deployment exercises.

> **This is a learning application, not a production-ready service.**
> It has no authentication or per-user data isolation: anyone with access to
> the API can operate on the shared journal entries. Keep it in a controlled
> learning environment and add appropriate access controls before exposing it
> publicly.

## Work on Your Own Fork

This repository is a starter template. Fork it to your GitHub account, clone
**your fork**, and do all your work and pull requests there.

**Do not open PRs against `learntocloud/journal-starter`.** They will be closed
without review. Your PRs should target `YOUR_USERNAME/journal-starter`.

## Prerequisites

On your host machine, you need:

- Git
- Docker Desktop, installed and running
- VS Code with the Dev Containers extension

The development container supplies Python and uv, and a separate container runs
PostgreSQL. You will install the application's dependencies during setup.

## Start Here

**Begin with [Getting Started](docs/setup.md)** to fork, clone, configure your
environment, and run the API.

Follow this learning path:

1. [Set up and run the API](docs/setup.md), then create and view an entry.
2. [Prepare your development workflow](docs/workflow.md): tools, tests, branches,
   commits, and PRs.
3. [Complete the development tasks](docs/tasks.md) in order, following each
   task's acceptance criteria.

All application and test commands run from the **project root inside the
development container**. Setup instructions explicitly identify commands that
belong on your host instead.

## What You Will Build

Creating entries, listing entries, deleting all entries, and database persistence
are provided. The starter also includes the update persistence and analysis
endpoint wiring; you complete the validation and LLM implementation.

Each journal entry records what you worked on, what you struggled with, and what
you intend to study next. See the [data schema](docs/tasks.md#data-schema).

| Task | Your work |
|------|-----------|
| [1: Logging](docs/tasks.md#task-1-logging-setup) | Configure application logging |
| [2a: GET single entry](docs/tasks.md#task-2a-get-single-entry-endpoint) | Fetch an entry by ID, or return 404 |
| [2b: DELETE single entry](docs/tasks.md#task-2b-delete-single-entry-endpoint) | Delete an entry by ID, or return 404 |
| [3: Input validation](docs/tasks.md#task-3-input-validation) | Validate creation and partial-update requests |
| [4: AI analysis](docs/tasks.md#task-4-ai-powered-entry-analysis) | Generate sentiment, a summary, and topics using a live LLM provider |
| [5: Cloud CLI](docs/tasks.md#task-5-cloud-cli-setup-manual) | Install and verify one cloud CLI in your devcontainer |

## What Completion Means

Satisfy every task's automated and manual acceptance criteria. Some tests fail
initially because the exercises are intentionally unfinished; do not modify the
supplied tests to make them pass.

Passing tests cover selected behaviors, not every possible bug. Task 4 also
requires a live provider check, and Task 5 requires manual CLI verification.
See [test coverage](docs/tasks.md#what-the-automated-tests-cover) and
[how CI works](docs/workflow.md#continuous-integration).

Database-backed tests erase entries only in the dedicated test database.
Never store personal entries there. Read the
[test database safety requirements](docs/workflow.md#test-database-safety)
before running tests.

## Guides and Reference

| Guide | Use it when you need to... |
|-------|----------------------------|
| [Getting Started](docs/setup.md) | Get from a fresh fork to a running API |
| [Development Workflow](docs/workflow.md) | Run checks and manage each task's branch and PR |
| [Development Tasks](docs/tasks.md) | Find implementation requirements and acceptance commands |
| [AI Analysis](docs/ai-analysis.md) | Configure a provider and implement Task 4's response contract |
| [Troubleshooting](docs/troubleshooting.md) | Diagnose errors, upgrade an existing devcontainer, or decide whether to restart or rebuild |
| [Upstream Synchronization](docs/upstream-sync.md) | Bring in template updates without deleting your fork or losing work |
| [Explore Your Database](docs/explore-database.md) | Connect to PostgreSQL and run queries directly |

## License

MIT License - see [LICENSE](LICENSE) for details.
