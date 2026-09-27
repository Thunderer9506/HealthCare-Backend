# HealthCare Backend — Detailed Documentation

## 1. Project Overview
Objective (from `Django Assignment_1.pdf`): Build a secure healthcare backend using Django, Django REST Framework (DRF), PostgreSQL, and JWT authentication (`djangorestframework-simplejwt`). The system allows user registration, login, and full CRUD management of patients, doctors, and patient-doctor mappings.

Audience: Engineers familiar with FastAPI who want to understand Django patterns.

---

## 2. Technology Stack
| Component | Version / Tool | Purpose |
|---|---|---|
| Django | 6.1.1 | Web framework |
| DRF | 3.18.1 | REST APIs |
| PostgreSQL | 15 (`psycopg2-binary`) | Production database |
| JWT Auth | `djangorestframework-simplejwt` 5.5.1 | Token-based auth |
| Password Hashing | `bcrypt` 5.0.0 | Secure password storage |
| WSGI Server | `gunicorn` 23.0.0 | Production server |
| Env Management | `python-dotenv` 1.1.0 | `.env` file loading |
| Containerization | Docker + `docker-compose.yml` | Production simulation |

---

## 3. Architecture & Design Patterns
### App Separation (like FastAPI APIRouters)
Django doesn't have `APIRouter`, but apps serve the same purpose:
- `auth_app/` — Authentication (register/login) → like an Auth Router
- `patients/` — Patient CRUD → Patient Router
- `doctors/` — Doctor CRUD → Doctor Router
- `mappings/` — Patient-Doctor assignments → Mapping Router
- `main/` — Health check (`/`) → System Router

### Authentication Dependency (DRF `IsAuthenticated`)
Every protected route uses:
```python
@permission_classes([IsAuthenticated])
```
This is Django's equivalent of FastAPI's `Depends(get_current_user)`. No route is accessible without a valid JWT `Authorization: Bearer <token>` header.

### DB Session Management (Django ORM)
Django manages DB connections per request automatically through middleware. Unlike FastAPI (where you explicitly create/close `Session` objects with context managers), Django opens a connection when a query is made and closes it at the end of the request. This is handled by `django.middleware.common.CommonMiddleware` and the request/response cycle — no manual session code is required.

---

## 4. Project Structure & File Explanations
```
HealthCare Backend/
├── .env.example              # Template environment variables
├── .claude/
│   └── plans/                 # Planning documentation
├── Django Assignment_1.pdf   # Original assignment spec
├── CLAUDE.md                 # Project memory/state tracking
├── Dockerfile                 # Production container image
├── README.md                  # This file
├── docker-compose.yml         # Multi-service orchestration (postgres + web)
├── manage_tests.py            # Single entry point: runs all 4 app test suites
├── manage.py                  # Django CLI (migrate, runserver, test, etc.)
├── requirements.txt           # Python dependencies (pinned versions)
├── test_memory.sqlite3        # Temporary SQLite file for quick in-memory checks
├── auth_app/                  # Authentication routes + User model
│   ├── migrations/             # Auto-generated DB schema changes
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Custom User (UUID, email username, bcrypt)
│   ├── tests.py                # 10 auth test cases
│   ├── urls.py                 # /api/auth/register/, /api/auth/login/
│   └── views.py                # JWT register/login + case-insensitive checks
├── doctors/                   # Doctor management
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Doctor (UUID, name, specialization)
│   ├── tests.py                # 10 doctor test cases
│   ├── urls.py                 # /api/doctors/
│   └── views.py                # CRUD with IsAuthenticated
├── main/                      # System health route
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py                 # / → health check
│   └── views.py                # Returns {"status":"healthy"}
├── mappings/                  # Patient-Doctor assignments
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Mapping (UUID, FK to Patient + Doctor, assigned_at)
│   ├── tests.py                # 10 mapping test cases
│   ├── urls.py                 # /api/mappings/
│   └── views.py                # CRUD assignments + get-by-patient doctors
├── patients/                  # Patient management
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py              # Patient (UUID, name, age, gender, created_by FK)
│   ├── tests.py                # 10 patient test cases
│   ├── urls.py                 # /api/patients/
│   └── views.py                # User-scoped CRUD with IsAuthenticated
└── healthcare_backend/        # Project settings (renamed from helloworld)
    ├── asgi.py                 # ASGI entry point
    ├── settings.py             # Central config (DB, auth model, REST framework, JWT)
    ├── urls.py                 # Root URL routing (includes auth, patients, doctors, mappings)
    └── wsgi.py                 # WSGI entry point
```

---

## 5. Database Models (Detailed)

### User (`auth_app/models.py`)
Inherits from Django's `AbstractBaseUser` + `PermissionsMixin`.

| Field | Type | Parameters | Why |
|---|---|---|---|
| `id` | UUIDField | `primary_key=True`, `default=uuid.uuid4`, `editable=False` | Unique identifier (not sequential) |
| `name` | CharField | `max_length=100`, `db_index=True`, no default | Required; indexed for queries |
| `email` | EmailField | `unique=True`, `db_index=True` | Login identifier; case-sensitive DB check handled manually |
| `password` | CharField | `max_length=128` | Stores `bcrypt` hashed value (never plain text) |
| `created_at` | DateTimeField | `default=timezone.now` | Audit timestamp |

**Notes**:
- `USERNAME_FIELD = 'email'` (login uses email, not username)
- `is_active` removed (no logout/deactivation route required by assignment)
- `groups` and `user_permissions` use custom `related_name` (`auth_app_user_set`, `auth_app_user_permissions_set`) to avoid clashes with Django's default `auth.User` model.

### Patient (`patients/models.py`)
| Field | Type | Params |
|---|---|---|
| `id` | UUIDField | Primary key |
| `name` | CharField | `max_length=100`, `db_index=True` |
| `age` | IntegerField | `null=True`, `blank=True` |
| `gender` | CharField | `max_length=10`, choices: `Male`/`Female`/`Other` |
| `created_by` | ForeignKey | `User`, `on_delete=CASCADE`, `related_name='patients'` |
| `created_at` | DateTimeField | `default=timezone.now` |

### Doctor (`doctors/models.py`)
| Field | Type | Params |
|---|---|---|
| `id` | UUIDField | Primary key |
| `name` | CharField | `max_length=100`, `db_index=True` |
| `specialization` | CharField | `max_length=100` |
| `created_at` | DateTimeField | `default=timezone.now` |

### Mapping (`mappings/models.py`)
| Field | Type | Params |
|---|---|---|
| `id` | UUIDField | Primary key |
| `patient` | ForeignKey | `Patient`, `on_delete=CASCADE`, `related_name='mappings'` |
| `doctor` | ForeignKey | `Doctor`, `on_delete=CASCADE`, `related_name='mappings'` |
| `assigned_at` | DateTimeField | `auto_now_add=True` |

---

## 6. Authentication Flow (JWT + Bcrypt)

### Register (`POST /api/auth/register/`)
1. Receives `name`, `email`, `password`.
2. Normalizes email to lowercase (`email.lower()`).
3. Checks for duplicates with case-insensitive query (`email__iexact`) — prevents `A@mail` vs `a@mail` duplicates.
4. Hashes password with `bcrypt.hashpw()`.
5. Creates user via `User.objects.create()` (stores original case email, hashed password).

### Login (`POST /api/auth/login/`)
1. Receives `email`, `password`.
2. Normalizes input email (`.lower()`).
3. Finds user via `email__iexact` (handles case differences).
4. Verifies hashed password with `bcrypt.checkpw()`.
5. Returns JWT `access` and `refresh` tokens via `RefreshToken.for_user()`.

### Protected Routes
Every route in `patients/`, `doctors/`, `mappings/` uses:
```python
@permission_classes([IsAuthenticated])
```
Without a valid `Authorization: Bearer <access_token>` header, DRF returns `401 Unauthorized`.

---

## 7. Route Reference (All APIs)

### Auth (`auth_app/urls.py`)
| Method | Path | Auth Required | Description |
|---|---|---|---|
| POST | `/api/auth/register/` | No | Register new user |
| POST | `/api/auth/login/` | No | Login, receive JWT |

### Patients (`patients/urls.py`)
| Method | Path | Auth | Note |
|---|---|---|---|
| POST | `/api/patients/` | Yes | Add patient (user-scoped) |
| GET | `/api/patients/` | Yes | List patient's own patients |
| GET | `/api/patients/<uuid:id>/` | Yes | Patient detail |
| PUT | `/api/patients/<uuid:id>/` | Yes | Update patient |
| DELETE | `/api/patients/<uuid:id>/` | Yes | Delete patient |

### Doctors (`doctors/urls.py`)
| Method | Path | Auth | Note |
|---|---|---|---|
| POST | `/api/doctors/` | Yes | Add doctor |
| GET | `/api/doctors/` | Yes | All doctors |
| GET | `/api/doctors/<uuid:id>/` | Yes | Doctor detail |
| PUT | `/api/doctors/<uuid:id>/` | Yes | Update doctor |
| DELETE | `/api/doctors/<uuid:id>/` | Yes | Delete doctor |

### Mappings (`mappings/urls.py`)
| Method | Path | Auth | Note |
|---|---|---|---|
| POST | `/api/mappings/` | Yes | Assign doctor → patient |
| GET | `/api/mappings/` | Yes | All mappings |
| GET | `/api/mappings/<uuid:patient_id>/doctors/` | Yes | Doctors for a patient |
| DELETE | `/api/mappings/<uuid:id>/` | Yes | Remove assignment |

---

## 8. Testing Strategy

### Test Distribution
- `auth_app/tests.py`: 10 cases (register success, missing fields, duplicate case-insensitive; login success, invalid password, missing field, wrong email, case-insensitive match)
- `patients/tests.py`: 10 cases (create, get, update, delete, missing fields, invalid IDs)
- `doctors/tests.py`: 10 cases (create, get, update, delete, missing fields, invalid IDs)
- `mappings/tests.py`: 10 cases (create, get, delete by mapping, get by patient, invalid IDs, missing fields)

### Running Tests
```bash
# All 30 at once (entry point)
python manage_tests.py

# Individual apps
python manage.py test auth_app.tests --verbosity=2
python manage.py test patients.tests --verbosity=2
python manage.py test doctors.tests --verbosity=2
python manage.py test mappings.tests --verbosity=2
```

Note: Full suite expects PostgreSQL running. `test_memory.sqlite3` exists for quick SQLite checks but is not required for normal test runs.

---

## 9. Docker Setup

### Build and Run
```bash
# Copy environment template
cp .env.example .env

# Start both services (postgres + web)
docker-compose up --build

# Run in background
docker-compose up -d
```

### Dockerfile Details
- Base: `python:3.11` (not slim — includes build dependencies for `psycopg2`)
- Installs `libpq-dev` and `gcc` before `pip install`
- Uses `gunicorn` as WSGI server bound to `0.0.0.0:8000`

### Environment Variables (`.env.example`)
```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/healthcare_db
DB_HOST=localhost
SECRET_KEY=django-insecure-change-me
DEBUG=True
DJANGO_SETTINGS_MODULE=healthcare_backend.settings
```
In `docker-compose.yml`, the `db` service provides PostgreSQL (`postgres:15`), and `DB_HOST=db` is injected into the web container so Django connects to the correct host.

---

## 10. Setup Instructions

### Local Development (requires PostgreSQL running locally)
```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Docker Development
```bash
docker-compose up --build
```
App runs at `http://localhost:8000/`.

---

## 11. Common Issues

- **Connection refused to localhost:5432**: PostgreSQL isn't running. Start it locally (`brew services start postgresql` or `service postgresql start`) or use `docker-compose up`.
- **`DB_HOST` not set in container**: The `web` service gets `DB_HOST=db` from `docker-compose.yml`. Without it, Django tries `localhost`, which fails inside the container.
- **Case-sensitive email duplicates**: Handled by `.lower()` + `email__iexact` in both register and login. Original case (`Alice@test.com`) is preserved in the DB.
- **Password never plain text**: `bcrypt.hashpw()` stores hashes; `bcrypt.checkpw()` verifies on login.

---

## 12. References
- Assignment PDF: `Django Assignment_1.pdf`
- Django Custom User Model docs
- DRF `IsAuthenticated` permission
- `djangorestframework-simplejwt` JWT docs
- `bcrypt` Python package docs
