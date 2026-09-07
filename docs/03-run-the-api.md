# Chapter 3: Run the API

[Home](../README.md) · **Chapter 3 of 10**

In this chapter, you will install the project dependencies, run the starter
tests, and start the API. Then you'll create your first journal entry.

## 1. Install the Project

1. We'll be using `uv` to install the Python packages this project depends on
   and run commands with those packages available. Install the application and
   development dependencies:

   ```bash
   uv sync
   ```

   This creates a `.venv` directory in the project root. A virtual environment
   keeps the project's Python packages separate from other projects.

2. Install the project's pre-commit hook:

   ```bash
   uv run pre-commit install
   ```

   A pre-commit hook runs checks before Git creates a commit. This project's
   hook runs Ruff, which checks Python code for issues such as unused imports
   and applies consistent formatting. You should see a message confirming that
   the hook was installed: `
pre-commit installed at .git/hooks/pre-commit`

3. In VS Code, open the Command Palette and select **Python: Select Interpreter**.
   Choose the interpreter at `.venv/bin/python`.

   If it is not listed, choose **Enter interpreter path** and select
   `.venv/bin/python` inside your project directory. The interpreter is the
   Python executable VS Code uses. Selecting this one makes editor tests and
   debugging use the same dependencies as `uv run`.

## 2. Run the Starter Tests

Your codebase has some functionality already implemented. The starter tests check that functionality.

1. Run the tests:

   ```bash
   uv run pytest -m 'not exercise'
   ```

   Pytest runs automated tests. The `-m 'not exercise'` option leaves out tests
   marked as unfinished exercises. These starter tests should pass. The full
   suite will not pass until you complete the capstone.

2. Read the test summary in the terminal. You should see `213 passed, 105 deselected`.

## 3. Start the API

1. Start the development server:

   ```bash
   uv run uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Uvicorn serves the FastAPI application defined in `api/main.py`. The
   `--reload` option restarts it when you save code changes. The host and port
   options let you reach it through the development container's forwarded port.
   Wait for the terminal to report that application startup is complete.

2. Another option to run the server is to use VS Code Run and Debug tool. We have provided a launch configuration for you, which you can review at `.vscode/launch.json` if you'd like. It is configured to run the same command as above. 

3. In the side panel, select Run and Debug, in the drop down select, **Python Debugger: FastAPI** configuration, and click the green play button. The server will start in a new terminal.

4. You can also use F5 to start the server. F5 will run whatever configuration is selected in the drop down. 

5. To stop the server, press `Ctrl+C` in the terminal where it is running or click the red square in the Run and Debug control.

Congratulations! You now know how to run and stop the API server.

## 4. Create Your First Entry

Make sure the server is running, then follow these steps to create a journal entry:

1. Open <http://localhost:8000/docs> in your browser. This page lets you send
   requests to the API without writing a separate client application.

2. Expand **POST `/entries`** and click **Try it out**. POST creates a new entry.
   Replace the request body with this made-up example:

   ```json
   {
     "work": "Started the journal API and explored its documentation",
     "struggle": "Understanding how requests reach the application",
     "intention": "Build the endpoint that retrieves one entry"
   }
   ```

   Use made-up, non-sensitive content throughout the capstone. Later, you will
   send sample journal content to an AI provider.

3. Click **Execute**. You should see HTTP status **201**, which means the entry
   was created. The response should include `"detail": "Entry created successfully"`
   and an `entry` object containing your text and a generated `id`.

4. Expand **GET `/entries`**, click **Try it out**, and then click **Execute**.
   GET retrieves data. You should see HTTP status **200**, which means the request
   succeeded, and your new entry in the `entries` list.

## Before You Continue

You should now have passing starter tests, a running API, and a made-up journal
entry visible through **GET `/entries`**. There is no pull request for this chapter.

---

[← Previous: Project setup](02-project-setup.md) ·
[Next: Build GET for one entry →](04-get-entry.md)
