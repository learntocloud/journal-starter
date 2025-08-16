# Project state — journal-starter
_Last updated: 2025-08-15_

## Snapshot
- Guide: https://learntocloud.guide/phase2/build-app
- Stack: FastAPI (async) • SQLAlchemy ORM (async) • PostgreSQL • Alembic • Pydantic v2 • pytest (AsyncClient + mocks)
- Pattern: Service–repository • Dependency-injected routes

## Progress (from last check)
1. Scaffolding & repo setup — ✅ Complete  
2. Environment & .env config — ✅ Complete (.env + app/core/config.py; Docker/DB configured)  
3. DB model & Alembic migration — ✅ Complete (entry table; migrations run)  
4. SQLAlchemy async integration — ✅ Complete  
5. Pydantic v2 schemas — ✅ Complete (ConfigDict + model_validate)  
6. Service/repository layer — ✅ Complete  
7. API routing (CRUD) — ✅ Complete (create/get/update/delete/list)  
8. Dependency injection — ✅ Complete (overrides testable)  
9. Router unit tests (mocked service) — ✅ Complete  
10. Service-layer unit tests — ✅ Complete  
11. Integration tests (real DB) — ⚪ In progress (smoke test added for POST /entries)  
12. API docs (OpenAPI) — ✅ Complete (FastAPI default)  
13. CORS, logging, healthcheck — ✅ Complete  
14. README, CI workflow, Dockerfile — ⚪ Final polish (verify)  
15. Deployment — ⚪ Not started

## Current step
- Finalize CI + README polish; decide whether to expand integration tests beyond the smoke test.

## Test status
- Summary: **21 passed** locally (`pytest -q` on 2025-08-15); **21 passed** in CI (commit `ad94fa7`, Python 3.11), coverage uploaded  
- Integration: basic POST /entries smoke test hitting real DB (localhost:5432) added  
- Notable failures/flakes: **none**

## Database & migrations
- Docker: **running (local)**; **CI uses Postgres service on 5432**
- Alembic head: **73f82b54943b**  
- Pending migrations: **0**  
- Note: local `alembic current` now works after aligning `.env` DSN with running container
- DB: Docker Postgres 16 on localhost:5432
- Alembic: current head 73f82b54943b (Add entry table)

## Open issues / TODOs
- [ ] Align local `.env` `DATABASE_URL` with CI DSN and re-run `alembic current`
- [ ] Add edge-case tests for service layer (validation errors, not-found, DB exceptions) — optional if integration coverage expanded
- [ ] Verify CI (workflow triggers, Python version, test step, coverage upload)
- [ ] README: add quick-start + `.env.example` instructions + Makefile targets
- [ ] (Optional) Expand integration tests to GET, PUT, DELETE endpoints
- [ ] (Optional) Choose deployment target and create app manifest

## Next actions (concrete)
1. Decide: expand integration tests now, or move to final polish phase.  
2. Run: `pytest -q` → keep “Test status” up to date.  
3. Review `.github/workflows/<ci>.yml` → confirm triggers, Python version, install/test steps, env vars for DB.  
4. Add/confirm `README.md` sections: Quick start, Makefile, `.env.example`, Testing, Migrations, API routes.
