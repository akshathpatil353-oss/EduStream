# EduStream Frontend

A responsive Next.js frontend for the EduStream academic learning platform. It includes student and instructor workspaces, authentication, course discovery/enrollment, instructor course creation and lecture upload, a course lecture library, and semantic search with cited source passages.

## Run the frontend

Requirements: Node.js 20.9+ and npm.

```bash
cd edustream-frontend
cp .env.example .env.local
npm install
npm run dev
```

Open <http://localhost:3000>. The app starts in demo mode and works without a backend. Demo accounts are available on the sign-in screen; no password is needed. Demo changes are stored in this browser's local storage. Choose **Connect live API** on the sign-in screen to use the FastAPI backend instead. Set `NEXT_PUBLIC_DEMO_MODE=false` in `.env.local` if you want live mode selected when the app first opens.

## Connect the FastAPI backend

The default API address is `http://127.0.0.1:8000`. Override it in `.env.local`:

```dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
NEXT_PUBLIC_DEMO_MODE=true
```

Run the backend separately from its project root:

```bash
uvicorn api:app --reload
```

The backend's CORS configuration allows `http://localhost:3000`. Use that exact frontend origin in development, or update the backend CORS allowlist for another origin. The API uses JWT bearer authentication. This frontend keeps the access token in browser local storage for this student-project demo; use an appropriately secured session strategy before production deployment.

## Backend contract used

The integration follows the supplied `api.py` and services:

| Feature | API contract |
|---|---|
| Register | `POST /auth/register` JSON `{full_name,email,password,role}`; response includes `user`. Registration does not issue a token. |
| Login | `POST /auth/login` JSON `{email,password}`; response includes `access_token`, `token_type`, and `user`. |
| Profile / role checks | `GET /auth/me`, `GET /student/dashboard`, `GET /instructor/dashboard` with `Authorization: Bearer <token>`. |
| Catalog | `GET /courses` → `{courses:[{course_id,course_code,course_name,description,instructor_id,instructor_name}]}`. |
| Enrolled / assigned courses | `GET /student/courses` or `GET /instructor/courses` → `{courses:[...]}`. |
| Create course | `POST /courses` JSON `{course_code,course_name,description}`; instructor identity comes from JWT. |
| Enroll | `POST /courses/{course_id}/enroll`; student identity comes from JWT. |
| Lecture upload | `POST /lectures/upload?course_id=<id>` multipart fields `file` (PDF/PPTX); instructor identity comes from JWT. |
| Lecture list | `GET /courses/{course_id}/lectures` → `{lectures:[{lecture_id,course_id,title,file_path,uploaded_at}]}` with any valid token. |
| Semantic search | `POST /search` JSON `{query,limit}` (limit 1–20) → `{results:[{lecture_title,chunk_text,chunk_index,similarity}]}`; student only. |

The UI surfaces API error details from FastAPI and handles pending and success states. Instructor-created courses are tied to the authenticated instructor in live mode. The API has no lecture download/view endpoint: its lecture list returns a backend-local `file_path`, which a browser cannot use as a safe, network-accessible file URL. Therefore the frontend can list lecture records and show search passages, but cannot open/download the original uploaded PDF/PPTX until the backend adds a route that serves authorized files.

## Backend and database prerequisites

The provided backend README requires Python 3.12, PostgreSQL 16, pgvector, Python dependencies, a `.env` with database values and `JWT_SECRET_KEY`, and a pre-created EduStream schema. `database.py` reads `DB_HOST` (default `localhost`), `DB_NAME` (default `edustream_db`), `DB_USER` (default `postgres`), `DB_PASSWORD`, and `DB_PORT` (default `5432`). `services/token_service.py` requires `JWT_SECRET_KEY`; it defaults `JWT_ALGORITHM` to `HS256` and token lifetime to 30 minutes.

The uploaded ZIP contains no schema SQL or database dump, so these frontend materials cannot provision or verify the database. The backend must be configured and its tables, indexes, vector extension, and supporting database objects created separately. Lecture upload and semantic search also depend on document extraction libraries, the Sentence Transformers model download/initialization, PostgreSQL, and pgvector. Backend credentials and the database were not supplied, so authenticated live requests and end-to-end upload/search against PostgreSQL are not verified here.

## Build

```bash
npm run build
npm start
```

## Presentation / demo guide

1. Run the frontend and open <http://localhost:3000>. It opens on the sign-in screen in demo mode.
2. Choose **Explore as student**. Show the overview, learning stats, course cards, and recent materials.
3. Open **Explore courses**, enroll in a course, then return to **My courses** and open its lecture library.
4. Open **Ask EduStream**, select a suggested question, and show the semantic-search passages with match scores and lecture/chunk sources. Demo results are clearly backed by sample data.
5. Sign out and choose **Explore as instructor**. Create a course and visit **Upload materials** to walk through the PDF/PPTX flow. In demo mode a selected file creates a local sample record; it does not contact a server.
6. For the live presentation, start FastAPI and PostgreSQL first, configure the database/schema and backend `.env`, then use **Connect live API** and real accounts. Confirm the API is healthy at <http://127.0.0.1:8000/health>.

The sample dashboard includes illustrative progress/study metrics because the backend does not provide learning analytics. Live course progress is a presentation placeholder, not a measured value.
