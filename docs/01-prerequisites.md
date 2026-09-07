# Chapter 1: Check the Prerequisites

[Home](../README.md) · **Chapter 1 of 10**

Before you begin, make sure you install:

- [Git](https://git-scm.com/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) and start it
- [Visual Studio Code](https://code.visualstudio.com/)
- The [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

You do not need to install Python, PostgreSQL, or uv. The development containers
provide them.

## Know Where Commands Run

You will use two terminals:

| Location | Use it for |
|----------|------------|
| Host machine | Cloning the repository, opening VS Code, and Docker commands |
| VS Code terminal inside the devcontainer | Python, uv, API, test, Git, and cloud CLI commands |

Later chapters identify the location when it matters. Unless stated otherwise,
run capstone commands from the project root inside the devcontainer.

## Before You Continue

Confirm Docker Desktop is running:

```bash
docker version
```

If that command cannot connect to Docker, start Docker Desktop before continuing.

---

[Next: Set up the project →](02-project-setup.md)
