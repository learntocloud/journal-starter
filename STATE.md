# Project state — journal-starter
_Last updated: 2025-08-16_

## Snapshot
- Guide: https://learntocloud.guide/phase2/build-app
- Stack: FastAPI (async) • SQLAlchemy ORM (async) • PostgreSQL • Alembic • Pydantic v2 • pytest (AsyncClient + mocks)
- Pattern: Service–repository • Dependency-injected routes

## Progress
1. Scaffolding & repo setup — ✅ Complete  
2. Environment & .env config — ✅ Complete (.env + app/core/config.py; Docker/DB configured)  
3. DB model & Alembic migration — ✅ Complete (entry table; migrations run)  
4. SQLAlchemy async integration — ✅ Complete  
5. Pydantic v2 schemas — ✅ Complete (ConfigDict + model_validate)  
6. Service/repository layer — ✅ Complete  
7. API routing (CRUD) — ✅ Complete (create/get/update/delete/list)  
8. Dependency injection — ✅ Complete (overrides testable)  
9. Router unit tests (mocked service) — ✅ Complete  
10. Service-layer unit tests — ✅ Complete (CRUD + edge cases)  
11. Integration tests (real DB) — ✅ Complete (green locally & in CI)  
12. API docs (OpenAPI) — ✅ Complete (FastAPI default)  
13. CORS, logging, healthcheck — ✅ Complete  
14. README, CI workflow, Dockerfile — ⚪ Needs polish/verify  
15. Deployment — ⚪ Not started

## Current step
- Polish README (quick start, `.env.example`, Makefile targets).
- Confirm CI coverage thresholds and workflow reliability.
- Decide on deployment target (Render, Fly.io, Railway, etc.).

## Test status
- Summary: **24 passed** locally (`pytest -q` on 2025-08-16); **24 passed** in CI, coverage uploaded  
- Coverage: ~90%+ (meets threshold, see CI)  
- Notable failures/flakes: **none**

## Database & migrations
- Docker: **stopped (local)**; **CI uses Postgres service on 5432**  
- Alembic head: **73f82b54943b**  
- Pending migrations: **0**  
- DB: Docker Postgres 16 on localhost:5432  
- Alembic: current head `73f82b54943b_add_entry_table`  

## Open issues / TODOs
- [ ] README polish: add quick-start, `.env.example`, Makefile targets, API usage examples  
- [ ] CI: confirm Python 3.11/3.12 matrix, keep coverage ≥90%  
- [ ] Deployment target + manifest  
- [ ] (Optional) Add load/perf tests for API  

## Next actions (concrete)
1. Finalize `README.md` → include Quick start, `.env.example`, Makefile, Testing, Migrations, API routes.  
2. Add minimal Makefile (`make run`, `make test`, `make migrate`).  
3. Keep CI workflow as-is, ensure coverage is enforced.  
4. Pick deployment target and create manifest (`Dockerfile` already present).  
