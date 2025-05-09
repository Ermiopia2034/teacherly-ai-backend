# Teacherly AI Backend

The backend for Teacherly AI, a platform to assist teachers with AI-powered tools for content creation, grading, and reporting.

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

   ```

4. Initialize the database:
   ```
   alembic upgrade head
   ```

5. Run the server:
   ```
   uvicorn app.main:app --reload
   ```

## Features

- Authentication with JWT
- Content creation with AI assistance
- Automated grading
- Report generation and distribution
- OCR for handwritten assignments

## Project Structure

The backend follows a modular structure with:
- API routers for endpoint definition
- Services for business logic
- Database models and CRUD operations
- Pydantic schemas for validation 