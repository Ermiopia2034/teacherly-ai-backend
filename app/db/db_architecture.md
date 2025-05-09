## Teacherly AI Toolkit: Database Entity & Relationship Documentation

This document outlines the database schema for the Teacherly AI Toolkit. It details each entity (table), its attributes (columns), and the relationships between entities. Understanding these relationships is crucial for implementing backend functionalities correctly, especially concerning data ownership and retrieval logic.

**Core ORM:** SQLAlchemy
**Database:** PostgreSQL

---

### 1. `User` Entity (`users` table)

Represents an individual who can log in to the system. Initially, this will primarily be teachers, but the `role` attribute allows for future expansion (e.g., Admins).

**Attributes:**

*   `id` (Integer, Primary Key, Auto-increment): Unique identifier for the user.
*   `email` (String, Unique, Indexed, Not Null): User's email address, used for login.
*   `hashed_password` (String, Not Null): Securely hashed password.
*   `full_name` (String, Nullable): Full name of the user.
*   `role` (Enum: `TEACHER`, `ADMIN`, Default: `TEACHER`, Not Null): Role of the user in the system.
*   `is_active` (Boolean, Default: `True`): Whether the user account is active and can log in.
*   `created_at` (DateTime, Server Default: `now()`): Timestamp of when the user was created.
*   `updated_at` (DateTime, On Update: `now()`): Timestamp of the last update to the user record.

**Relationships:**

*   **One-to-Many with `Student`:** A `User` (teacher) can have many `Student` records.
    *   *Foreign Key:* `students.teacher_id` references `users.id`.
    *   *SQLAlchemy Relationship:* `User.students` (accesses all students for this teacher).
*   **One-to-Many with `Content`:** A `User` (teacher) can create many `Content` items (materials, exams, quizzes).
    *   *Foreign Key:* `content.teacher_id` references `users.id`.
    *   *SQLAlchemy Relationship:* `User.content_items` (accesses all content created by this teacher).

**Backend Functionality Relevance:**

*   **Authentication & Authorization:**
    *   Login: Validates `email` and `hashed_password`.
    *   Registration: Creates new user records.
    *   JWTs will contain `user.id` to identify the logged-in user.
    *   The `role` will be used for role-based access control if implemented.
    *   `is_active` determines if a user can log in.
*   **Data Ownership:** The `id` is the primary key for linking teacher-specific data across other tables. All operations that create or retrieve data specific to a teacher will use this `id`.
*   **User Profile Management:** Storing and updating `full_name`.

---

### 2. `Student` Entity (`students` table)

Represents a student enrolled under a specific teacher.

**Attributes:**

*   `id` (Integer, Primary Key, Auto-increment): Unique identifier for the student.
*   `full_name` (String, Not Null): Full name of the student.
*   `grade_level` (String, Nullable): The grade or academic level of the student (e.g., "Grade 10").
*   `parent_email` (String, Nullable): Email address of the student's parent/guardian, used for sending reports.
*   `teacher_id` (Integer, Foreign Key to `users.id`, Not Null): Links the student to their teacher. **Crucial for data scoping.**
*   `created_at` (DateTime, Server Default: `now()`): Timestamp of when the student record was created.
*   `updated_at` (DateTime, On Update: `now()`): Timestamp of the last update to the student record.

**Relationships:**

*   **Many-to-One with `User`:** Many `Student` records belong to one `User` (teacher).
    *   *SQLAlchemy Relationship:* `Student.teacher` (accesses the teacher of this student).
*   **One-to-Many with `Grade`:** A `Student` can have many `Grade` records (one for each assessment).
    *   *Foreign Key:* `grades.student_id` references `students.id`.
    *   *SQLAlchemy Relationship:* `Student.grades` (accesses all grades for this student).
*   **One-to-Many with `Attendance`:** A `Student` can have many `Attendance` records.
    *   *Foreign Key:* `attendance.student_id` references `students.id`.
    *   *SQLAlchemy Relationship:* `Student.attendance_records` (accesses all attendance records for this student).

**Backend Functionality Relevance:**

*   **Student Management:** CRUD operations for students, always scoped by `teacher_id`.
*   **Grading & Reporting:**
    *   Linking grades to specific students.
    *   Retrieving student lists for generating reports or viewing class performance.
    *   Using `parent_email` for the "Email Report to Parents" feature.
*   **Attendance Tracking:** Linking attendance records to specific students.
*   **Data Scoping:** Backend logic must ensure a teacher can only access/manage students linked to their `teacher_id`.

---

### 3. `Content` Entity (`content` table)

Represents teaching materials, exams, or quizzes created by a teacher.

**Attributes:**

*   `id` (Integer, Primary Key, Auto-increment): Unique identifier for the content item.
*   `title` (String, Not Null): Title of the material, exam, or quiz.
*   `content_type` (Enum: `MATERIAL`, `EXAM`, `QUIZ`, Not Null): Specifies the type of content.
*   `description` (Text, Nullable): A brief description of the content.
*   `data` (JSON, Nullable): Flexible field to store the actual content.
    *   For `MATERIAL`: Could store structured lesson plans, text, links to resources, etc.
    *   For `EXAM`/`QUIZ`: Could store a list of questions, question types, options, point values.
*   `answer_key` (JSON, Nullable): Primarily for `EXAM`/`QUIZ`. Stores correct answers, marking schemes.
*   `teacher_id` (Integer, Foreign Key to `users.id`, Not Null): Links the content to the teacher who created it. **Crucial for data scoping.**
*   `created_at` (DateTime, Server Default: `now()`): Timestamp of content creation.
*   `updated_at` (DateTime, On Update: `now()`): Timestamp of the last update.

**Relationships:**

*   **Many-to-One with `User`:** Many `Content` items are created by one `User` (teacher).
    *   *SQLAlchemy Relationship:* `Content.teacher` (accesses the teacher who created this content).
*   **One-to-Many with `Grade`:** One `Content` item (if it's an `EXAM` or `QUIZ`) can have many `Grade` records associated with it (one per student who took it).
    *   *Foreign Key:* `grades.content_id` references `content.id`.
    *   *SQLAlchemy Relationship:* `Content.grades` (accesses all grades for this specific exam/quiz).

**Backend Functionality Relevance:**

*   **Teaching Material Generation:**
    *   Storing AI-generated lesson plans, worksheets in the `data` field.
    *   `content_type` will be `MATERIAL`.
*   **Exam/Quiz Preparation:**
    *   Storing AI-generated questions and structure in `data`.
    *   Storing correct answers and marking guidelines in `answer_key`.
    *   `content_type` will be `EXAM` or `QUIZ`.
*   **Exam/Quiz Grading:** The `answer_key` is retrieved from this table to be used by the AI for automated grading.
*   **Content Management:** CRUD operations for content, always scoped by `teacher_id`.
*   **RAG System (Indirectly):** While the curriculum for RAG is in a Vector DB, the *generated* content based on RAG + LLM is stored here.

---

### 4. `Grade` Entity (`grades` table)

Represents a student's grade for a specific piece of content (an exam or quiz).

**Attributes:**

*   `id` (Integer, Primary Key, Auto-increment): Unique identifier for the grade record.
*   `score` (Float, Not Null): The numerical score the student received.
*   `max_score` (Float, Nullable): The maximum possible score for the assessment this grade is for.
*   `feedback` (Text, Nullable): AI-generated or teacher-provided feedback for the student's performance.
*   `grading_date` (DateTime, Server Default: `now()`): Timestamp of when the grading was performed/recorded.
*   `student_id` (Integer, Foreign Key to `students.id`, Not Null): Links the grade to a specific student.
*   `content_id` (Integer, Foreign Key to `content.id`, Not Null): Links the grade to the specific exam/quiz.
*   `created_at` (DateTime, Server Default: `now()`): Timestamp of when the grade record itself was created in the system.

**Relationships:**

*   **Many-to-One with `Student`:** Many `Grade` records can belong to one `Student`.
    *   *SQLAlchemy Relationship:* `Grade.student` (accesses the student this grade belongs to).
*   **Many-to-One with `Content`:** Many `Grade` records can be associated with one `Content` item (the specific exam/quiz).
    *   *SQLAlchemy Relationship:* `Grade.content` (accesses the exam/quiz this grade is for).

**Backend Functionality Relevance:**

*   **Exam/Quiz Grading (Automated & Manual):**
    *   Storing the results of AI-powered grading (`score`, `feedback`).
    *   Allowing teachers to manually enter or override grades.
*   **Grade Reporting:**
    *   Fetching all grades for a student, or for a class on a specific assessment.
    *   Used to compile data for Excel exports and email reports to parents.
*   **Data Scoping:** Access to grades is implicitly scoped through the `student_id` and `content_id`, which are both linked back to a specific `teacher_id`. Backend logic must ensure teachers only see grades related to their students and their content.

---

### 5. `Attendance` Entity (`attendance` table)

Records a student's attendance for a specific date.

**Attributes:**

*   `id` (Integer, Primary Key, Auto-increment): Unique identifier for the attendance record.
*   `attendance_date` (Date, Not Null): The date for which attendance is being recorded.
*   `status` (Enum: `PRESENT`, `ABSENT`, `LATE`, `EXCUSED`, Not Null): The attendance status of the student.
*   `notes` (Text, Nullable): Optional notes regarding the attendance (e.g., reason for absence if excused).
*   `student_id` (Integer, Foreign Key to `students.id`, Not Null): Links the attendance record to a specific student.
*   `created_at` (DateTime, Server Default: `now()`): Timestamp of when the attendance record was created.

**Relationships:**

*   **Many-to-One with `Student`:** Many `Attendance` records can belong to one `Student`.
    *   *SQLAlchemy Relationship:* `Attendance.student` (accesses the student this attendance record belongs to).

**Backend Functionality Relevance:**

*   **Attendance Keeping:**
    *   Allowing teachers to mark attendance for their students.
    *   Storing historical attendance data.
*   **Reporting:**
    *   Including attendance information in student reports.
*   **Data Scoping:** Access to attendance records is scoped through the `student_id`, which is linked to a `teacher_id`. Backend logic must enforce this.
