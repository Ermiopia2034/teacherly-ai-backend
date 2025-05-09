# Teacherly AI Backend

The backend for Teacherly AI, a platform to assist teachers with AI-powered tools for content creation, grading, and reporting.

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory with the following variables:
   ```
   # Database
   DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/teacherly

   # JWT
   JWT_SECRET=your_secret_key_here
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30

   # Google Gemini API
   GEMINI_API_KEY=your_gemini_api_key

   # OCR.space API
   OCR_API_KEY=your_ocr_api_key

   # SMTP Email Service
   SMTP_HOST=smtp.example.com
   SMTP_PORT=587
   SMTP_USER=your_email@example.com
   SMTP_PASSWORD=your_email_password
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