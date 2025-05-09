**Core Backend Architecture:**

1.  **FastAPI Application (Async Python Web Framework):**
    *   Serves as the entry point for all API requests.
    *   Handles request validation (using Pydantic schemas), routing, and response formatting.
    *   All I/O-bound operations (database calls, external API calls, email sending) will be `async/await`.

2.  **Authentication & Authorization Module (JWT-based with Data Ownership):**
    *   **Password Hashing:** Uses `passlib` with `bcrypt` to hash passwords before storing them in PostgreSQL and to verify passwords during login.
    *   **JWT Generation & Validation:**
        *   On successful login, generates a JWT containing the `user_id`.
        *   FastAPI **dependency** (`get_current_active_user`) will be used in *all protected API routes*. This dependency:
            *   Extracts the JWT from the `Authorization` header.
            *   Verifies the JWT's signature and expiry.
            *   Retrieves the user from the database based on the `user_id` in the token.
            *   Raises an `HTTPException` (401 Unauthorized) if the token is invalid or the user doesn't exist.
    *   **Data Ownership Enforcement:**
        *   All database models representing user-owned data (e.g., teaching materials, exams, student records linked to a teacher, grades) will have a `teacher_id` (or `user_id`) foreign key.
        *   All service and database layer functions that access or modify these resources will require the `current_user`'s ID and will filter queries by this ID (e.g., `SELECT * FROM content WHERE teacher_id = :current_user_id`).
        *   If a user attempts to access data not belonging to them, an `HTTPException` (403 Forbidden or 404 Not Found) will be raised.

3.  **API Routers (Modular Endpoints):**
    *   Separate routers for different functionalities (e.g., `auth_router.py`, `content_router.py`, `grading_router.py`, `report_router.py`).
    *   Each protected route function will include `current_user: User = Depends(get_current_active_user)` in its signature.

4.  **Service Modules (Business Logic Layer - Async with Ownership):**
    *   **`auth_service.py`:** Handles user registration, login.
    *   **`ai_service.py`:** Interfaces with the Google Gemini LLM API (async HTTP requests using `httpx`).
    *   **`rag_service.py`:** Connects to **ChromaDB** (as the chosen Vector Database client) to retrieve curriculum context.
    *   **`ocr_service.py`:** Interfaces with the **OCR.space API** (async HTTP requests using `httpx`).
    *   **`db_postgres_service.py` (and/or `crud.py` modules per entity):**
        *   Handles all interactions with PostgreSQL using **SQLAlchemy with the `asyncpg` driver**.
        *   All functions will accept `user_id` (or the `current_user` object) to ensure queries are scoped to the correct user's data.
    *   **`email_service.py`:**
        *   Uses Python's `aiosmtplib` (for async SMTP) to connect to the **external SMTP server** (credentials and server details from environment variables).
        *   Sends email reports to parents, ensuring that the teacher initiating the send has the authority over the student data being sent.
    *   **`report_service.py`:**
        *   Aggregates data by querying `db_postgres_service.py`, always passing the `current_user.id`.
        *   Generates Excel files using `XlsxWriter`.

5.  **Database Layer:**
    *   **PostgreSQL (Async Access via SQLAlchemy & `asyncpg`):**
        *   Stores structured data: `User` (with `hashed_password`), `Student` (linked to a `teacher_id`), `Content` (teaching materials/exams with `teacher_id`), `Grade` (linked to a student and content, thus implicitly to a teacher), `Attendance` (linked to a student).
    *   **ChromaDB (Vector Database - Application Read-Only):**
        *   Stores embeddings of the Ethiopian MOE curriculum. Populated by a separate script. The application only retrieves from it.

6.  **Configuration Management:**
    *   Pydantic's `BaseSettings` will be used to load configuration from environment variables (via a `.env` file) for database URLs, API keys (Gemini, OCR.space), JWT secret key, SMTP server details (host, port, username, password).

7.  **Pydantic Schemas:**
    *   Used for strict request body validation, response serialization, and data transfer objects.

**Project Structure (Specific):**

```
teacherly-ai-backend/
├── app/                        # Main application code
│   ├── __init__.py
│   ├── main.py                 # FastAPI app instantiation, global middleware, router inclusion
│   │
│   ├── api/                    # API Routers (endpoints)
│   │   ├── __init__.py
│   │   ├── deps.py             # FastAPI dependencies (get_current_active_user)
│   │   ├── auth_router.py      # Login, Register (doesn't use get_current_active_user for all routes)
│   │   ├── content_router.py   # All routes use get_current_active_user
│   │   ├── grading_router.py   # All routes use get_current_active_user
│   │   └── report_router.py    # All routes use get_current_active_user
│   │
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── ai_service.py
│   │   ├── rag_service.py      # Uses ChromaDB client
│   │   ├── ocr_service.py      # Uses OCR.space API via httpx
│   │   ├── email_service.py    # Uses aiosmtplib with external SMTP config
│   │   └── report_service.py
│   │
│   ├── db/                     # Database related code
│   │   ├── __init__.py
│   │   ├── database.py         # PostgreSQL async session/engine (SQLAlchemy+asyncpg), ChromaDB client setup
│   │   ├── models/             # SQLAlchemy models (PostgreSQL table definitions)
│   │   │   ├── __init__.py
│   │   │   ├── user_model.py     # (id, email, hashed_password, ...)
│   │   │   ├── student_model.py  # (id, name, parent_email, teacher_id -> FK to User)
│   │   │   ├── content_model.py  # (id, title, type, data, teacher_id -> FK to User)
│   │   │   ├── grade_model.py    # (id, score, feedback, student_id -> FK, content_id -> FK)
│   │   │   └── attendance_model.py # (id, date, status, student_id -> FK)
│   │   └── crud/                 # CRUD operations for PostgreSQL (SQLAlchemy)
│   │       ├── __init__.py
│   │       ├── crud_user.py
│   │       ├── crud_student.py   # All functions take teacher_id for scoping
│   │       ├── crud_content.py   # All functions take teacher_id for scoping
│   │       └── crud_grade.py     # All functions ensure operations are for students of the teacher
│   │
│   ├── schemas/                # Pydantic schemas for request/response validation
│   │   ├── __init__.py
│   │   ├── token_schema.py
│   │   ├── user_schema.py      # (UserCreate, UserRead, etc.)
│   │   ├── student_schema.py
│   │   ├── content_schema.py
│   │   └── grade_schema.py
│   │
│   ├── core/                   # Core utilities and configuration
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic Settings (loads from .env)
│   │   └── security.py         # Password hashing (passlib), JWT utilities
│   │
│   └── utils/                  # General utility functions
│       └── __init__.py
│
├── alembic/                    # Alembic migrations for PostgreSQL (SQLAlchemy)
│   └── ...
├── scripts/                    # Utility scripts
│   └── populate_vector_db.py   # Script to process curriculum and load into ChromaDB
│
├── tests/                      # Unit and integration tests
│   └── ...
│
├── .env                        # Environment variables (DB_URL, API_KEYS, JWT_SECRET, SMTP_HOST, SMTP_USER, SMTP_PASSWORD etc.)
├── .gitignore
├── requirements.txt            # Python dependencies (fastapi, uvicorn, sqlalchemy, asyncpg, passlib[bcrypt], python-jose[cryptography], pydantic[email], httpx, aiosmtplib, chromadb, XlsxWriter, python-dotenv)
└── README.md
```

**Key Operational Flow (Example: Teacher creating content):**

1.  Teacher logs in via `/api/auth/login`. `auth_service.py` verifies credentials, `security.py` generates a JWT. Token returned to frontend.
2.  Frontend stores JWT securely. For subsequent requests, it includes `Authorization: Bearer <jwt_token>` header.
3.  Teacher requests to create teaching material via POST to `/api/content/material`.
4.  `content_router.py` route function has `current_user: User = Depends(get_current_active_user)`.
    a.  `deps.py::get_current_active_user` validates the token and fetches the `User` object.
5.  `content_router.py` calls a service function, e.g., `content_service.create_teaching_material_async(data_from_request, current_user)`.
6.  `content_service.py`:
    a.  `await`s call to `rag_service.get_context_for_topic_async(topic)`.
    b.  `await`s call to `ai_service.generate_material_from_llm_async(prompt, rag_context)`.
    c.  `await`s call to `crud_content.create_content_async(db_session, content_data, teacher_id=current_user.id)`.
7.  Response is returned to the teacher.

This architecture provides a clear, modular, and secure (within the scope of a graduation project) foundation, incorporating all your specified adjustments.