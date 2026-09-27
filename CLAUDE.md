# HealthCare Backend Project

Project: Django backend for healthcare application (Assignment_1.pdf)
User: First-time Django user, experienced with FastAPI
Goal: Build REST APIs with JWT auth, patient/doctor management, PostgreSQL

Stack: Django 6.1, DRF, PostgreSQL, djangorestframework-simplejwt
Current status:
- Basic Hello World route (main app) completed
- Auth routes separated into auth_app (like FastAPI APIRouter)
- JWT auth configured (register/login at /api/auth/ with access/refresh tokens)
- PostgreSQL case-sensitive email handled: register uses `email__iexact` to reject duplicates (A@mail vs a@mail), login normalizes input with `.lower()` before `get(email__iexact=...)` to find correct user, original case preserved in DB
- Users model: name (CharField max=100, db_index=True, no default/null), email (EmailField unique+db_index), password (CharField max=128), created_at (DateTimeField default=timezone.now), is_active removed (no logout route)
- README.md created documenting PostgreSQL case-sensitive email problem and `iexact`/`.lower()` solution
- Passwords hashed with bcrypt: `bcrypt.hashpw()` in register, `bcrypt.checkpw()` in login (no plain text stored)
- requirements.txt created with Django, DRF, simplejwt, psycopg2-binary, bcrypt, pyjwt
- Patients/Doctors/Mappings apps created with UUID models, DRF IsAuthenticated dependency, URL routing
- Dockerfile + docker-compose.yml created (postgres + web services)
- manage_tests.py entry point runs all 4 app test suites
- Temporary SQLite file (test_memory.sqlite3) created for in-memory testing
- Main folder converted to health check route (`/` -> `{'status':'healthy'}`)
- .env.example + docker-compose updated with env_file
- requirements.txt updated (gunicorn, python-dotenv)
- README rewritten with full docs: best practices, setup, tests, APIs
- Temp SQLite file kept (`test_memory.sqlite3`) for quick in-memory testing
- DB_HOST env fix: settings reads `DB_HOST` (defaults localhost, set to `db` in docker-compose) so Django connects to correct PostgreSQL service
- CLAUDE.md updated frequently

Reference: See Django Assignment_1.pdf for full requirements.
