# Chapter 2: Set Up the Project

[Home](../README.md) · **Chapter 2 of 10**

In this chapter, you will fork the repository, create its local configuration,
and open the development container. Then you'll add a cloud CLI in your first pull
request.

## 1. Fork and Clone

1. On GitHub.com, fork `learntocloud/journal-starter`.

2. Once the fork is created, go to your fork's **Actions** tab at
   `https://github.com/YOUR_USERNAME/journal-starter/actions`, replacing `YOUR_USERNAME`
   with your GitHub username. If you see "Workflows aren’t being run on this forked
   repository," click **I understand my workflows, go ahead and enable them** to
   enable the workflows for your fork.

3. On your host machine, clone your fork, replacing `YOUR_USERNAME` with your GitHub username:

   ```bash
   git clone https://github.com/YOUR_USERNAME/journal-starter.git
   ```

4. Change into the project directory:

   ```bash
   cd journal-starter
   ```

5. Verify that your fork is the `origin` remote:

   ```bash
   git remote -v
   ```

   `origin` should point to `YOUR_USERNAME/journal-starter`.

6. Open your cloned fork in VS Code:

   ```bash
   code .
   ```

## 2. Create the Environment File

1. Once the project is open in VS Code, open the integrated terminal with
   `` Ctrl + ` `` (backtick).

2. Make sure you are in the project root:

   ```bash
   pwd
   ```

   It should print the path to the `journal-starter` directory on your host machine.

3. The sample environment file contains secret values for local development.
   Copy the sample environment file to `.env`:

   ```bash
   cp .env-sample .env
   ```

4. Do not make any changes to the `.env` file yet.

5. An important security note: the `.env` file is ignored by Git. Confirm this by running:

   ```bash
   git check-ignore .env
   ```

   The terminal should print `.env`, which means it is ignored by Git. You can also
   confirm this by opening the `.gitignore` file and searching for `.env` with
   `Cmd/Ctrl + F`. You should see it listed there. Do not change this.

## 3. Open the Development Container

This project uses development containers (Dev Containers), which provide a consistent development environment.

1. In VS Code, open the Command Palette with `Cmd/Ctrl + Shift + P` and select
   **Dev Containers: Reopen in Container**.

2. VS Code will reload and build the development container. This may take a few minutes the first time.

3. Once the container is built, VS Code will reopen in the container. You should see
   an indicator in the bottom-left corner that says **Dev Container: Journal Starter**.

4. Open a new VS Code terminal and run:

   ```bash
   pwd
   ```

   It should print `/workspaces/journal-starter`.

5. If you'd like, take some time now to review how the development container is
   configured. The configuration files are in the `.devcontainer` folder. The
   `devcontainer.json` file defines the container and its features, and the
   `docker-compose.yml` file defines the services that run alongside it.

If the container does not open, use the
[troubleshooting guide](reference/troubleshooting.md#development-container-will-not-open).

## 4. Add a Cloud CLI in Your First Pull Request

Time for your first task! You will add a cloud CLI to the development container and create a pull request.

1. Before starting any task, it's important to make sure your working tree is clean.
   A working tree is the directory that contains the files for your project. A clean
   working tree means there are no uncommitted changes. Starting with a clean working
   tree helps keep changes for a task separate from other tasks or work in progress.
   At this point, you should not have made any changes to tracked files, and your
   `.env` file should be ignored by Git. Run the following command to check whether
   your working tree is clean:

   ```bash
   git status
   ```

   You should see:

   ```text
   On branch main
   Your branch is up to date with 'origin/main'.

   nothing to commit, working tree clean
   ```

2. It's also important to make sure your local `main` branch is up to date with the
   remote `main` branch. First, run the following command to make sure you are on
   the `main` branch:

   ```bash
   git checkout main
   ```

3. Now run the following command to make sure your local `main` branch is up to date
   with the remote `main` branch:

   ```bash
   git pull origin main
   ```

4. Now it's time to create a new branch for your task. Run the following command to
   create a new branch called `setup/cloud-cli` and switch to it:

   ```bash
   git checkout -b setup/cloud-cli
   ```

5. Open the `.devcontainer/devcontainer.json` file and uncomment exactly one cloud
   CLI feature. You can choose from Azure, AWS, or GCP. For example, to add the
   Azure CLI, uncomment the following line:

   ```json
   "ghcr.io/va-h/devcontainers-features/azure-cli": {}
   ```

6. Because you have changed the development container configuration, you need to
   rebuild the container for the change to take effect. Choose
   **Dev Containers: Rebuild Container** in the VS Code Command Palette.

7. After the container is rebuilt, open a new VS Code terminal and run the command
   for your chosen cloud CLI to verify that it is installed:

   ```bash
   az --version
   # or: aws --version
   # or: gcloud --version
   ```

8. Now that you have verified that the cloud CLI is installed, it's time to review
   your changes. In VS Code, open the Source Control view by clicking the
   **Source Control** icon in the left sidebar or by pressing `Ctrl + Shift + G`.
   You should see that the `.devcontainer.json` file is listed as a
   changed file. You may also see `devcontainer-lock.json`

9. Lines that are added or modified will be highlighted in green, and lines that
   are removed will be highlighted in red. Review the changes to make sure they
   are correct.

10. Now it's time to prepare your changes for a commit. Run the following command
    to add the changes to the staging area:

    ```bash
    git add .
    ```

11. Now it's time to commit your changes. Run the following command to commit your changes with a descriptive message:

    ```bash
    git commit -m "Add a cloud CLI to the devcontainer"
    ```

12. Now that you have committed your changes, it's time to push your changes to your
    fork on GitHub. Run the following command to push your changes to the
    `setup/cloud-cli` branch on your fork:

    ```bash
    git push -u origin setup/cloud-cli
    ```

13. Now that you have pushed your changes to your fork, it's time to open a pull
    request. Go to your fork's **Pull requests** tab at
    `https://github.com/YOUR_USERNAME/journal-starter/pulls`, replacing `YOUR_USERNAME`
    with your GitHub username.

14. You should see a message that says "setup/cloud-cli has recent pushes less than a minute ago."

15. Click **Compare & pull request**. Make sure the base branch is `main` on
    **your fork**, not `learntocloud/journal-starter`, and the compare branch is
    `setup/cloud-cli`.

16. Add a title and description for your pull request. The title should be
    descriptive, and the description should explain what changes you made and why.
    For this one, you can use:

    **Title:** Add a cloud CLI to the devcontainer

    **Description:** This pull request adds a cloud CLI to the development container.
    The cloud CLI is installed as a feature in the development container configuration
    file. This change allows developers to use the cloud CLI in the development
    container without having to install it manually.

17. We'll be using labels to select which tests to run in CI. Add a label called
    `task:setup` to your pull request. If the label does not exist, create it.
    You can do this by clicking the **Labels** section on the right side of the
    pull request page, then clicking **Create new label**. Name the label
    `task:setup` and give it a color. Then click **Create label**. After creating
    the label, select it for your pull request.

18. Click **Create pull request** to create your pull request.

19. The repository includes a GitHub Actions workflow in `ci.yaml` that runs tests
    on pull requests. The workflow will run automatically when you create your pull
    request. You can view its progress by clicking the **Actions** tab in your fork.
    You should see a workflow called **CI** running. Click the workflow to view the
    details. You can also view the logs of each job by clicking the job name.
    See [Testing and CI](reference/testing-and-ci.md) for how labels select tests.

20. Once the workflow is complete, you should see a green checkmark next to your pull
    request indicating that the tests passed. If the tests failed, click **Details**
    to view the logs and fix any issues. After fixing the issues, push your changes
    to the `setup/cloud-cli` branch, and the workflow will run again.

21. Once the workflow passes, you can merge your pull request. Click **Merge pull request**,
    then click **Confirm merge**. After merging, you can delete the `setup/cloud-cli`
    branch by clicking **Delete branch**.

## Before You Continue

1. After merging your pull request, switch back to `main`:

   ```bash
   git checkout main
   ```

2. Pull the merged changes into your local `main` branch:

   ```bash
   git pull origin main
   ```

You should now have a running development container with one cloud CLI installed and
your setup pull request merged into your fork.

---

[← Previous: Prerequisites](01-prerequisites.md) ·
[Next: Run the API →](03-run-the-api.md)
