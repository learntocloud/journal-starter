# Topic 5: Capstone - Journal API

Welcome to your Python capstone project! You'll be working with a **FastAPI + PostgreSQL** application that helps people track their daily learning journey. This will prepare you for deploying to the cloud in the next phase.

By the end of this capstone, your API should be working locally and ready for cloud deployment.

## Table of Contents

- [Getting Started](#-getting-started)
- [Development Tasks](#-development-tasks-your-work)
- [Data Schema](#-data-schema)
- [AI Analysis Reference](#-ai-analysis-reference)
- [Explore Your Database](#-explore-your-database-optional)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Getting Started

### Prerequisites

- Git installed on your machine
- Docker Desktop installed and running
- VS Code with the Dev Containers extension

### 1. Fork and Clone the Repository

1. **Fork this repository** to your GitHub account by clicking the "Fork" button
1. **Clone your fork** to your local machine:

   ```bash
   git clone https://github.com/YOUR_USERNAME/journal-starter.git
   ```

1. Move into the project directory:

   ```bash
   cd journal-starter
   ```

1. **Open in VS Code**:

   ```bash
   code .
   ```

### 2. Configure Your Environment (.env)

Environment variables live in a `.env` file (which is **git-ignored** so you don't accidentally commit secrets). This repo ships with a template named `.env-sample`.

1. Copy the sample file to create your real `.env`:

   ```bash
   cp .env-sample .env
   ```

### 3. Set Up Your Development Environment

1. **Install the Dev Containers extension** in VS Code (if not already installed)
2. **Reopen in container**: When VS Code detects the `.devcontainer` folder, click "Reopen in Container"
   - Or use Command Palette (`Cmd/Ctrl + Shift + P`): `Dev Containers: Reopen in Container`
3. **Wait for setup**: The API container will automatically install Python, dependencies, and configure your environment.
   The PostgreSQL Database container will also automatically be created.

### 4. Verify the PostgreSQL Database Is Running

In a terminal outside of VS Code, run:

   ```bash
      docker ps
   ```

You should see the postgres service running.

### 5. Run the API

Back in the VS Code terminal, verify you're in the project root:

   ```bash
     pwd
   ```
You should see a path ending with `journal-starter`.

Then start the API with:


   ```bash
     ./start.sh
   ```

### 6. Test Everything Works! 🎉

1. **Visit the API docs**: http://localhost:8000/docs
1. **Create your first entry** In the Docs UI Use the POST `/entries` endpoint to create a new journal entry.
1. **View your entries** using the GET `/entries` endpoint to see what you've created!

**🎯 Once you can create and see entries, you're ready to start the development tasks!**

## 🎯 Development Tasks (Your Work!)

You'll use **feature branches** and **Pull Requests (PRs)** for each task. Complete these tasks in your forked repository using feature branches.

### 1. Logging Setup

- Branch: `feature/logging-setup`
- [ ] Configure logging in `api/main.py`

### 2. API Implementation

#### Task 2a: GET Single Entry Endpoint

- Branch: `feature/get-single-entry`
- [ ] Implement **GET /entries/{entry_id}** in `api/routers/journal_router.py`

#### Task 2b: DELETE Single Entry Endpoint

- Branch: `feature/delete-entry`
- [ ] Implement **DELETE /entries/{entry_id}** in `api/routers/journal_router.py`

### 3. AI-Powered Entry Analysis

- Branch: `feature/ai-analysis`
- [ ] Implement `analyze_journal_entry()` in `api/services/llm_service.py`
- [ ] Implement **POST /entries/{entry_id}/analyze** in `api/routers/journal_router.py`

### 4. Data Model Improvements (Optional)

- Branch: `feature/data-model-improvements`  
- [ ] Add validators to `api/models/entry.py`

### 5. Cloud CLI Setup (Required for Deployment)

- Branch: `feature/cloud-cli-setup`
- [ ] Uncomment one CLI tool in `.devcontainer/devcontainer.json`

## 📊 Data Schema

Each journal entry follows this structure:

| Field       | Type      | Description                                | Validation                   |
|-------------|-----------|--------------------------------------------|------------------------------|
| id          | string    | Unique identifier (UUID)                   | Auto-generated               |
| work        | string    | What did you work on today?                | Required, max 256 characters |
| struggle    | string    | What's one thing you struggled with today? | Required, max 256 characters |
| intention   | string    | What will you study/work on tomorrow?      | Required, max 256 characters |
| created_at  | datetime  | When entry was created                     | Auto-generated UTC           |
| updated_at  | datetime  | When entry was last updated                | Auto-updated UTC             |

## 🤖 AI Analysis Reference

### The `/entries/{id}/analyze` Endpoint

This endpoint analyzes a journal entry using your chosen LLM and returns:
- **Sentiment**: positive, negative, or neutral
- **Summary**: 2-sentence summary of the entry
- **Topics**: 2-4 key topics mentioned

**Example Request:**
```bash
POST /entries/123e4567-e89b-12d3-a456-426614174000/analyze
```

**Example Response:**
```json
{
  "entry_id": "123e4567-e89b-12d3-a456-426614174000",
  "sentiment": "positive",
  "summary": "The learner made progress with FastAPI and database integration. They're excited to continue learning about cloud deployment.",
  "topics": ["FastAPI", "PostgreSQL", "API development", "cloud deployment"],
  "created_at": "2025-12-25T10:30:00Z"
}
```

### LLM Provider Setup

1. **Read the documentation** for your chosen provider:
   - [OpenAI](https://platform.openai.com/docs) | [Anthropic](https://docs.anthropic.com) | [Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/) | [AWS Bedrock](https://docs.aws.amazon.com/bedrock/) | [GCP Vertex AI](https://cloud.google.com/vertex-ai/docs)

2. **Add required environment variables** to your `.env` file

3. **Add your SDK** to `api/requirements.txt` and run `pip install -r api/requirements.txt`

## 🗄️ Explore Your Database (Optional)

Want to see your data directly in the database? You can connect to PostgreSQL using VS Code's PostgreSQL extension:

### 1. Install PostgreSQL Extension

1. **Install the PostgreSQL extension** in VS Code (search for "PostgreSQL" by Chris Kolkman)
2. **Restart VS Code** after installation

### 2. Connect to Your Database

1. **Open the PostgreSQL extension** (click the PostgreSQL icon in the sidebar)
2. **Click "Add Connection"** or the "+" button
3. **Enter these connection details**:
   - **Host name**: `postgres`
   - **User name**: `postgres`
   - **Password**: `postgres`
   - **Port**: `5432`
   - **Connection Type**: `Standard/No SSL`
   - **Database**: `career_journal`
   - **Display name**: `Journal Starter DB` (or any name you prefer)

### 3. Explore Your Data

1. **Expand your connection** in the PostgreSQL panel
2. **Left-click on "Journal Starter DB" to expand**
3. **Right-click on "career_journal"**
4. **Select "New Query"**
5. **Type this query** to see all your entries:

   ```sql
   SELECT * FROM entries;
   ```

6. **Run the query** to see all your journal data! (Ctrl/Cmd + Enter OR use the PostgreSQL command pallete: Run Query)

You can now explore the database structure, see exactly how your data is stored, and run custom queries to understand PostgreSQL better.

## 🔧 Troubleshooting

**If the API won't start:**

- Make sure the PostgreSQL container is running: `docker ps`
- Check the container logs: `docker logs your-postgres-container-name`
- Restart the database: `docker restart your-postgres-container-name`

**If you can't connect to the database:**

- Verify the `.env` file exists and has the correct DATABASE_URL
- Make sure Docker Desktop is running
- Try restarting the dev container: `Dev Containers: Rebuild Container`

**If the dev container won't open:**

- Ensure Docker Desktop is running
- Install the "Dev Containers" extension in VS Code
- Try: `Dev Containers: Rebuild and Reopen in Container`

## 🤝 Contributing

We welcome contributions to improve this capstone project! Open an issue and we can plan from there.

### Reporting Issues

Found a bug or have a suggestion? Please [open an issue](https://github.com/learntocloud/journal-starter/issues) with:

- **Clear description** of the problem or suggestion
- **Steps to reproduce** (for bugs)
- **Expected vs actual behavior**
- **Environment details** (OS, Docker version, etc.)

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Attribution

If you use this project as a foundation for your own work, we'd appreciate a link back to this repository, but it's not required.
