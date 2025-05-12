# Teacherly AI Backend - Development Guidelines

This document outlines the current state of the Teacherly AI backend, highlights recent fixes, and provides guidelines for future development to ensure consistency and prevent common issues.

## Current Status (As of May 12, 2025)

-   **Framework:** FastAPI
-   **Database:** PostgreSQL (via SQLAlchemy and asyncpg)
-   **Migrations:** Alembic
-   **Authentication:** Working JWT-based authentication using HttpOnly cookies.
    -   Registration (`/api/auth/register`)
    -   Login (`/api/auth/login`) - Uses OAuth2PasswordRequestForm (expecting `username` and `password` form fields).
    -   Logout (`/api/auth/logout`) - Clears the cookie.
    -   Get Current User (`/api/auth/users/me`) - Dependency (`get_current_user`) verifies the token from the cookie.
-   **CORS:** Configured in [`app/main.py`](./app/main.py) to allow requests from the frontend origin (`http://localhost:3001`) with credentials.
-   **Pydantic:** Using Pydantic v2. Schemas intended for ORM conversion **must** use `from_attributes = True` in their `Config` subclass.

## Recent Fixes & Key Points

1.  **JWT Configuration:** The JWT secret key and algorithm are defined in [`app/core/config.py`](./app/core/config.py) as `JWT_SECRET_KEY` and `ALGORITHM` respectively. Both token creation (`create_access_token`) and decoding (`decode_access_token`) in [`app/core/security.py`](./app/core/security.py) have been updated to use these correct names.
    -   **Guideline:** Always refer to settings via the `settings` object imported from `app.core.config`. Ensure names match between `config.py` and usage.
2.  **Pydantic V2 ORM Mode:** Schemas that need to be created from SQLAlchemy models (e.g., `UserRead` in [`app/schemas/user_schema.py`](./app/schemas/user_schema.py)) must include `from_attributes = True` in their inner `Config` class. The old `orm_mode = True` is deprecated.
    -   **Guideline:** When creating Pydantic schemas that will map from database models, always include `class Config: from_attributes = True`.
3.  **CORS for Credentials:** When the frontend needs to send credentials (like cookies, which it does for authentication via `withCredentials: true`), the backend's CORS configuration cannot use `allow_origins=["*"]`. It must explicitly list the allowed frontend origins (currently `["http://localhost:3001"]` in [`app/main.py`](./app/main.py)).
    -   **Guideline:** If frontend origins change or if deploying to production, update the `allow_origins` list in [`app/main.py`](./app/main.py) accordingly. Never use `"*"` with `allow_credentials=True`.
4.  **Passlib/Bcrypt Versioning:** A warning related to `passlib` trying to read `bcrypt.__about__.__version__` was silenced by downgrading `bcrypt` to version `4.0.1` (`pip install bcrypt==4.0.1`). This version is compatible with `passlib>=1.7.4`.
    -   **Guideline:** Keep `bcrypt==4.0.1` unless `passlib` is updated and specifically requires or supports a newer `bcrypt` version without warnings. Avoid direct upgrades of `bcrypt` beyond `4.0.1` while using `passlib` 1.7.x.

## Configuration

-   Environment variables are loaded from a `.env` file in the backend root using `python-dotenv` within [`app/core/config.py`](./app/core/config.py).
-   Pydantic's `BaseSettings` is used in [`app/core/config.py`](./app/core/config.py) to validate and manage settings.
-   Key settings include `DATABASE_URL`, `JWT_SECRET_KEY`, `ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`.
-   **Guideline:** Add any new required configuration variables to the `.env` file and define them in the `Settings` class in `config.py`. Ensure the `.env` file is included in `.gitignore`.

## Running the Backend (Development)

1.  Ensure you have Python 3.11+ and PostgreSQL installed.
2.  Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate # Linux/macOS
    # .\venv\Scripts\activate # Windows
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    pip install bcrypt==4.0.1 # Ensure specific bcrypt version
    ```
4.  Set up your `.env` file with `DATABASE_URL`, `JWT_SECRET_KEY`, etc.
5.  Apply database migrations (if needed):
    ```bash
    alembic upgrade head
    ```
6.  Run the development server:
    ```bash
    python -m app.main
    ```
    The server will run on `http://localhost:8000` with auto-reload enabled.

## Adding New Features

1.  **Router:** Define API endpoints in a new file within `app/api/` (e.g., `app/api/student_router.py`). Use `APIRouter` from FastAPI.
2.  **Schemas:** Define request/response models using Pydantic v2 in `app/schemas/` (e.g., `app/schemas/student_schema.py`). Remember `from_attributes = True` if converting from ORM models.
3.  **CRUD Operations:** Implement database interaction logic in `app/db/crud/` (e.g., `app/db/crud/crud_student.py`). Use SQLAlchemy core/ORM async operations.
4.  **Models:** Define database table structures in `app/db/models/` (e.g., `app/db/models/student_model.py`).
5.  **Migrations:** If you add or modify database models, generate a new migration:
    ```bash
    alembic revision --autogenerate -m "Description of changes"
    ```
    Then apply it:
    ```bash
    alembic upgrade head
    ```
6.  **Register Router:** Include the new router in [`app/main.py`](./app/main.py) using `app.include_router(...)`.
7.  **Dependencies:** If new packages are needed, add them to `requirements.txt` and reinstall (`pip install -r requirements.txt`). Ensure compatibility, especially around core libraries like `passlib`/`bcrypt`.

By following these guidelines, development should proceed smoothly, leveraging the existing structure and avoiding the pitfalls encountered previously.