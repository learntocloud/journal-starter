# Journal Starter API

[![CI](https://github.com/cfergile/journal-starter/actions/workflows/test.yml/badge.svg)](https://github.com/cfergile/journal-starter/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/cfergile/journal-starter/branch/main/graph/badge.svg)](https://codecov.io/gh/cfergile/journal-starter)

An educational **FastAPI + SQLAlchemy (async) CRUD API** for managing journal entries.  
This project is part of the [Learn to Cloud Guide](https://learntocloud.guide) capstone portfolio.

---

## 🚀 Features

- **FastAPI** backend with async endpoints
- **SQLAlchemy ORM (async)** for database access
- **Alembic** for migrations
- **Service–repository pattern** for clean architecture
- **PostgreSQL** database (Dockerized)
- **pytest** with coverage for router + service layers
- **GitHub Actions CI** with PostgreSQL service & Codecov integration

---

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- PostgreSQL (local or via Docker)

### Clone & Install
```bash
git clone https://github.com/cfergile/journal-starter.git
cd journal-starter
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
