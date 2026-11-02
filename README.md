# EduStream
### Smart Academic Portal with AI-Powered Semantic Lecture and Resource Retrieval

EduStream is a smart academic portal designed to simplify academic resource management and improve how students access information from lecture materials.

The platform combines a relational database with vector-based semantic search to provide an organized academic environment where instructors can manage courses and upload learning materials, while students can enroll in courses and retrieve relevant information from lecture documents using natural-language queries.

---

## 1. Project Overview

Traditional academic portals primarily organize learning resources using folders, filenames, and course categories. Finding a particular concept inside lengthy lecture notes or presentations can require students to manually search through multiple documents.

EduStream addresses this problem by integrating **semantic search** with a structured academic management system.

The platform uses:
- PostgreSQL for structured academic data.
- pgvector for storing and searching vector embeddings.
- Sentence Transformers for generating text embeddings.
- FastAPI for backend services and API communication.
- Next.js for the frontend interface.

The system retrieves relevant lecture passages based on the semantic meaning of a student's query rather than relying only on exact keyword matches.

## 2. Key Features

### Student Features
- Student registration and login.
- Secure authentication using JWT.
- Student dashboard.
- View available courses.
- Enroll in courses.
- Access enrolled course information.
- Search lecture materials using natural-language queries.
- View relevant passages retrieved from uploaded lecture documents.

### Instructor Features
- Instructor registration and login.
- Instructor dashboard.
- Create and manage courses.
- Upload lecture documents.
- Process uploaded PDF and PPTX files.
- Extract text and divide it into smaller chunks.
- Generate embeddings for lecture content.
- Make lecture materials available for semantic retrieval.

### AI-Powered Semantic Search
- Text extraction from lecture documents.
- Text chunking with overlapping sections.
- Embedding generation using Sentence Transformers.
- Vector storage using PostgreSQL and pgvector.
- Similarity-based retrieval using cosine distance.
- Retrieval of the most relevant lecture passages.

---

## 3. Technology Stack

| Component | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL 16 |
| Vector Database Extension | pgvector |
| Authentication | JWT |
| Password Security | Password hashing |
| Embedding Model | sentence-transformers/all-MiniLM-L6-v2 |
| Vector Index | HNSW |
| Document Processing | PyPDF, python-pptx |
| API Communication | REST API |
| Version Control | Git and GitHub |

---

## 4. System Architecture

EduStream follows a client-server architecture.

```text
                 STUDENT / INSTRUCTOR
                          |
                          v
                 NEXT.JS FRONTEND
                   (React + TS)
                          |
                          v
                    FASTAPI BACKEND
                          |
             +------------+------------+
             |            |            |
             v            v            v
        Authentication  Course      Document
           Service      Service    Processing
             |            |            |
             |            |            v
             |            |       Text Extraction
             |            |            |
             |            |            v
             |            |        Text Chunking
             |            |            |
             |            |            v
             |            |       Embedding Model
             |            |            |
             +------------+------------+
                          |
                          v
                    POSTGRESQL
                          |
                   +------+------+
                   |             |
                   v             v
              Relational      pgvector
                Tables         Storage
                   |             |
                   |             v
                   |        HNSW Index
                   |             |
                   +------+------+
                          |
                          v
                   SEMANTIC SEARCH
                          |
                          v
                 RELEVANT PASSAGES
                          |
                          v
                   NEXT.JS FRONTEND
```

---

## 5. Project Structure

```text
EduStream/
│
├── backend/
│   ├── services/
│   │   ├── auth_dependency.py
│   │   ├── auth_service.py
│   │   ├── course_service.py
│   │   ├── document_processor.py
│   │   ├── embedding_service.py
│   │   ├── password_service.py
│   │   ├── semantic_search.py
│   │   ├── storage_service.py
│   │   ├── text_chunker.py
│   │   └── token_service.py
│   │
│   ├── uploads/
│   ├── api.py
│   ├── database.py
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .gitignore
│
├── edustream-frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── lib/
│   │   └── api.ts
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── next.config.mjs
│   ├── tsconfig.json
│   ├── .env.example
│   └── README.md
│
├── database_schema.sql
├── .gitignore
├── LICENSE
└── README.md
```

---

## 6. Database Design

EduStream uses PostgreSQL as its primary relational database and pgvector for vector similarity search.

### Main Database Tables

| Table | Purpose |
|---|---|
| `users` | Stores student and instructor information. |
| `courses` | Stores course information. |
| `enrollments` | Maintains student-course relationships. |
| `lectures` | Stores uploaded lecture material metadata. |
| `lecture_chunks` | Stores extracted and segmented lecture text. |
| `lecture_embeddings` | Stores vector representations of lecture chunks. |

### Database Relationships

- A user can be associated with multiple enrollments.
- A course can have multiple enrolled students.
- Enrollments connect students and courses through a many-to-many relationship.
- A course can contain multiple lecture materials.
- Lecture materials are divided into text chunks.
- Each text chunk has an associated embedding for semantic retrieval.

### Database Components

The project also uses:

- Primary keys and foreign keys for data integrity.
- Foreign key constraints and cascading operations where configured.
- A database view named `student_course_details`.
- A database function named `get_student_course_count`.
- A trigger named `lecture_timestamp_trigger`.
- An HNSW index for efficient vector similarity searches.

The complete database schema is available in `database_schema.sql`.

---

## 7. Semantic Search Workflow

One of the primary features of EduStream is its semantic lecture retrieval system.

### Document Processing

When an instructor uploads a lecture document:

1. The backend receives the uploaded document.
2. Text is extracted from the PDF or PPTX file.
3. Extracted text is divided into smaller chunks.
4. Overlapping sections are maintained to preserve contextual continuity.
5. Each chunk is passed to the embedding model.
6. The generated embeddings are stored in PostgreSQL using pgvector.

### Query Processing

When a student searches for a topic:

1. The student enters a natural-language query.
2. The backend generates an embedding for the query.
3. The query embedding is compared against stored lecture embeddings.
4. Cosine distance is used to identify semantically similar chunks.
5. The most relevant passages are retrieved.
6. Retrieved passages and their relevance information are returned to the frontend.

### Embedding Model

EduStream uses:

`sentence-transformers/all-MiniLM-L6-v2`

The model generates 384-dimensional sentence embeddings.

### Vector Similarity

The system uses cosine distance to compare query and document embeddings.

The PostgreSQL pgvector operator used for cosine distance is:

```sql
<=>
```

The HNSW index helps improve vector similarity search performance.

**Note:** The current implementation focuses on semantic retrieval of relevant lecture passages. It does not use an LLM to generate conversational answers or summaries.

---

## 8. Installation and Setup

### Prerequisites

Install the following before running the project:

- Python 3.12 or later.
- Node.js 20 or later.
- npm.
- PostgreSQL 16.
- pgvector PostgreSQL extension.
- Git.

### Step 1: Clone the Repository

```bash
git clone https://github.com/akshathpatil353-oss/EduStream.git
```

Navigate into the project:

```bash
cd EduStream
```

### Step 2: Database Setup

1. Install PostgreSQL.
2. Ensure the pgvector extension is installed.
3. Create a database named `edustream_db`.
4. Connect to the database.
5. Execute the database schema.

Create the database:

```sql
CREATE DATABASE edustream_db;
```

Connect to it:

```sql
\c edustream_db
```

Enable pgvector if it is not already enabled by the schema:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Execute the schema file from PowerShell:

```powershell
psql -U postgres -d edustream_db -f .\database_schema.sql
```

---

## 9. Backend Setup

Navigate to the backend directory:

```powershell
cd backend
```

### Create a Virtual Environment

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### Install Dependencies

```powershell
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file using `.env.example` as a reference.

Example configuration:

```env
DB_HOST=localhost
DB_NAME=edustream_db
DB_USER=postgres
DB_PASSWORD=your_postgres_password
DB_PORT=5432

JWT_SECRET_KEY=replace_with_a_random_secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace the example values with your local configuration.

**Never commit your actual `.env` file or credentials to GitHub.**

### Run the Backend

```powershell
uvicorn api:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 10. Frontend Setup

Open another terminal and navigate to the frontend directory:

```powershell
cd edustream-frontend
```

### Install Dependencies

```powershell
npm install
```

### Configure Environment Variables

Create `.env.local` using `.env.example` as a reference.

Example:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_DEMO_MODE=false
```

### Run the Frontend

```powershell
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

Make sure the backend is running before using the frontend.

---

## 11. Running the Complete Application

EduStream requires both the backend and frontend services to be running.

| Service | Command | URL |
|---|---|---|
| Backend | `uvicorn api:app --reload` | http://127.0.0.1:8000 |
| API Documentation | Available through FastAPI | http://127.0.0.1:8000/docs |
| Frontend | `npm run dev` | http://localhost:3000 |

Recommended application workflow:

1. Start PostgreSQL.
2. Start the FastAPI backend.
3. Start the Next.js frontend.
4. Log in as an instructor.
5. Create a course.
6. Upload lecture documents.
7. Allow the backend to process the documents and generate embeddings.
8. Log in as a student.
9. Enroll in a course.
10. Enter a natural-language query in the semantic search interface.
11. Review the relevant lecture passages returned by the system.

---

## 12. Security and Data Management

The project incorporates the following security and data management practices:

- JWT-based authentication.
- Password hashing instead of storing plaintext passwords.
- Role-based access control for student and instructor operations.
- Environment variables for sensitive configuration.
- Relational database constraints for data integrity.
- Protected backend routes.
- CORS configuration for frontend-backend communication.

Users should configure their own database credentials and JWT secret before running the application.

---

## 13. Future Enhancements

Potential improvements include:

- LLM-based answer generation using retrieved lecture passages.
- Automatic lecture summarization.
- Conversational academic assistant.
- Improved document extraction and formatting.
- Advanced search filters by course, lecture, and topic.
- Support for additional document formats.
- Improved ranking and retrieval evaluation.
- Academic progress analytics and personalized recommendations.

---

## 14. Contributors

**Project:** EduStream – Smart Academic Portal with AI Semantic Lecture and Resource Retrieval

Developed as an academic project at PES University.

---

## 15. License

This repository is distributed under the GNU Lesser General Public License v2.1 (LGPL-2.1).

See the `LICENSE` file for the complete license terms.

---

**EduStream – Making academic knowledge easier to organize, discover, and access.**
