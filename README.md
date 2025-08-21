# Journal API

[![CI](https://github.com/cfergile/journal-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/cfergile/journal-starter/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/your-username/journal-starter/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/journal-starter)

A FastAPI-based CRUD Journal API built as part of the **Learn to Cloud Guide** capstone project.  
The goal: practice Python, APIs, databases, and testing in one cohesive project.

---

## 🎯 Objectives

**Core objectives (capstone scope):**
- Build a REST API with FastAPI  
- Implement CRUD endpoints for journal entries  
- Store data in PostgreSQL  
- Use Alembic for migrations  
- Test with pytest + httpx.AsyncClient  

**Extended objectives (added by me):**
- Containerize with Docker & Docker Compose  
- Run Postgres in a container (instead of installing locally)  
- Provide reproducible dev/test environments  

---

## 🚀 Features

- **POST** `/entries/` — create a journal entry  
- **GET** `/entries/` — list all entries  
- **GET** `/entries/{id}` — get a single entry  
- **PUT** `/entries/{id}` — update an entry  
- **DELETE** `/entries/{id}` — delete an entry  
- **GET** `/healthz` — health check  

Each entry includes:
- `work` — what you worked on today  
- `struggle` — something you struggled with  
- `intention` — what you’ll work on tomorrow  
- `id`, `created_at`, `updated_at`  

---

## 🛠 Setup Options

### 1. Local Setup (capstone default)

**Requirements**
- Python 3.11+  
- PostgreSQL running locally  
- Install dependencies: `pip install -r requirements.txt`

**Steps**
```bash
git clone https://github.com/your-username/journal-starter.git
cd journal-starter

cp .env.example .env

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

alembic upgrade head

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: [http://localhost:8000](http://localhost:8000)

---

### 2. Docker Compose Setup (extended option)

This goes beyond the original capstone, demonstrating containerization skills.

**Requirements**
- Docker & Docker Compose

**Steps**
```bash
git clone https://github.com/your-username/journal-starter.git
cd journal-starter

cp .env.example .env

docker compose up -d --build

docker compose exec web alembic upgrade head
```

API available at: [http://localhost:8000](http://localhost:8000)

---

## 🧪 Testing

```bash
pytest -q
```

---

## ⚙️ Environment Variables

See `.env.example` for configuration.

```ini
# Database
DB_HOST=db          # use 'localhost' if running locally
DB_PORT=5432
DB_NAME=journal
DB_USER=postgres
DB_PASSWORD=postgres

# Optional: full DSN (overrides pieces above)
# DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/journal
```

---

## 📦 Tech Stack

- FastAPI (async API framework)  
- SQLAlchemy 2.0 ORM (async engine)  
- Alembic (migrations)  
- PostgreSQL (database)  
- Docker Compose (optional dev setup)  
- pytest + httpx.AsyncClient (testing)  

---

## 📚 Learning Outcomes

- Met the original capstone objectives (API, CRUD, DB, tests)  
- Extended with Dockerized deployment for reproducibility and cloud readiness  
- Practiced modern Python backend development with async stack  
