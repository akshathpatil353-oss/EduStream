import os
import uuid

from fastapi import File, UploadFile
from services.semantic_search import search_lectures
from services.document_processor import extract_document_text
from services.text_chunker import split_text_into_chunks
from services.embedding_service import generate_embeddings
from services.storage_service import save_lecture_data
from services.course_service import (
    get_all_courses,
    get_course_by_id,
    create_course,
    enroll_student,
    get_student_courses,
    get_instructor_courses,
    get_course_lectures
)
from services.auth_dependency import (
    get_current_user,
    require_student,
    require_instructor
)
from fastapi import Depends, FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from services.token_service import create_access_token

from services.auth_service import register_user, login_user

app = FastAPI(
    title="EduStream API",
    description="Backend API for EduStream Academic Portal",
    version="1.0.0"
)

# CORS configuration for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request models

class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class CreateCourseRequest(BaseModel):
    course_code: str
    course_name: str
    description: str | None = None

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 5
# Health check

@app.get("/health")
def health_check():
    return {
        "status": "success",
        "message": "EduStream backend is running!"
    }


# User registration

@app.post("/auth/register")
def register(request: RegisterRequest):
    try:
        user = register_user(
            full_name=request.full_name,
            email=str(request.email),
            password=request.password,
            role=request.role
        )

        return {
            "status": "success",
            "message": "Registration successful!",
            "user": user
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


# User login


@app.post("/auth/login")
def login(request: LoginRequest):
    user = login_user(
        email=str(request.email),
        password=request.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password."
        )

    # Generate JWT access token
    access_token = create_access_token(
        user_id=user["user_id"],
        role=user["role"]
    )

    return {
        "status": "success",
        "message": "Login successful!",
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
# Authentication test endpoint

@app.get("/auth/me")
def get_my_profile(current_user=Depends(get_current_user)):
    return {
        "message": "Authentication successful!",
        "user": current_user
    }


# Student-only endpoint

@app.get("/student/dashboard")
def student_dashboard(student=Depends(require_student)):
    return {
        "message": "Welcome to the student dashboard!",
        "user_id": student["user_id"],
        "role": student["role"]
    }


# Instructor-only endpoint

@app.get("/instructor/dashboard")
def instructor_dashboard(instructor=Depends(require_instructor)):
    return {
        "message": "Welcome to the instructor dashboard!",
        "user_id": instructor["user_id"],
        "role": instructor["role"]
    }

# Course Management APIs

@app.get("/courses")
def list_courses():
    try:
        courses = get_all_courses()

        return {
            "status": "success",
            "total_courses": len(courses),
            "courses": courses
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve courses."
        )


@app.get("/courses/{course_id}")
def course_details(course_id: int):
    try:
        course = get_course_by_id(course_id)

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found."
            )

        return {
            "status": "success",
            "course": course
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve course details."
        )

# Create a new course (Instructor only)

@app.post("/courses", status_code=201)
def add_course(
    request: CreateCourseRequest,
    instructor=Depends(require_instructor)
):
    try:
        if not request.course_code.strip():
            raise HTTPException(
                status_code=400,
                detail="Course code cannot be empty."
            )

        if not request.course_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Course name cannot be empty."
            )

        course = create_course(
            course_code=request.course_code,
            course_name=request.course_name,
            description=request.description,
            instructor_id=instructor["user_id"]
        )

        return {
            "status": "success",
            "message": "Course created successfully!",
            "course": course
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Course creation error:", error)
        raise HTTPException(
            status_code=400,
            detail="Unable to create course. Check whether the course code already exists."
        )

# Student course enrollment

@app.post("/courses/{course_id}/enroll", status_code=201)
def enroll_in_course(
    course_id: int,
    student=Depends(require_student)
):
    try:
        # Check whether the course exists
        course = get_course_by_id(course_id)

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found."
            )

        # Enroll the authenticated student
        enrollment = enroll_student(
            student_id=student["user_id"],
            course_id=course_id
        )

        if enrollment is None:
            raise HTTPException(
                status_code=409,
                detail="You are already enrolled in this course."
            )

        return {
            "status": "success",
            "message": "Successfully enrolled in course!",
            "enrollment": enrollment
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Enrollment error:", error)
        raise HTTPException(
            status_code=500,
            detail="Unable to enroll in course."
        )

# Get courses enrolled by the logged-in student

@app.get("/student/courses")
def list_student_courses(
    student=Depends(require_student)
):
    try:
        courses = get_student_courses(
            student_id=student["user_id"]
        )

        return {
            "status": "success",
            "total_courses": len(courses),
            "courses": courses
        }

    except Exception as error:
        print("Student courses error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve enrolled courses."
        )

# Get courses assigned to the logged-in instructor

@app.get("/instructor/courses")
def list_instructor_courses(
    instructor=Depends(require_instructor)
):
    try:
        courses = get_instructor_courses(
            instructor_id=instructor["user_id"]
        )

        return {
            "status": "success",
            "total_courses": len(courses),
            "courses": courses
        }

    except Exception as error:
        print("Instructor courses error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve instructor courses."
        )

# Upload lecture materials (Instructor only)

@app.post("/lectures/upload", status_code=201)
async def upload_lecture(
    course_id: int,
    file: UploadFile = File(...),
    instructor=Depends(require_instructor)
):
    upload_directory = "uploads"

    try:
        # Check whether the course exists
        course = get_course_by_id(course_id)

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found."
            )

        # Ensure the instructor owns this course
        if course["instructor_id"] != instructor["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="You can only upload lectures to your own courses."
            )

        # Validate file extension
        extension = os.path.splitext(file.filename or "")[1].lower()

        if extension not in [".pdf", ".pptx"]:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and PPTX files are supported."
            )

        # Read uploaded file
        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty."
            )

        # Create upload directory
        os.makedirs(upload_directory, exist_ok=True)

        # Generate a unique filename
        unique_filename = f"{uuid.uuid4().hex}{extension}"
        file_path = os.path.join(upload_directory, unique_filename)

        # Save uploaded file
        with open(file_path, "wb") as uploaded_file:
            uploaded_file.write(file_content)

        try:
            # Extract text
            extracted_text = extract_document_text(file_path)

            if not extracted_text.strip():
                raise ValueError("No readable text found in the document.")

            # Split text into chunks
            chunks = split_text_into_chunks(extracted_text)

            if not chunks:
                raise ValueError("Unable to generate text chunks.")

            # Generate embeddings
            embeddings = generate_embeddings(chunks)

            # Save lecture, chunks and embeddings
            lecture_id = save_lecture_data(
                title=file.filename,
                file_path=file_path,
                course_id=course_id,
                chunks=chunks,
                embeddings=embeddings
            )

        except Exception:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise

        return {
            "status": "success",
            "message": "Lecture uploaded and processed successfully!",
            "lecture_id": lecture_id,
            "course_id": course_id,
            "filename": file.filename,
            "total_chunks": len(chunks)
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Lecture upload error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to upload and process lecture."
        )

    finally:
        await file.close()

# Get lectures belonging to a course

@app.get("/courses/{course_id}/lectures")
def list_course_lectures(
    course_id: int,
    current_user=Depends(get_current_user)
):
    try:
        course = get_course_by_id(course_id)

        if course is None:
            raise HTTPException(
                status_code=404,
                detail="Course not found."
            )

        lectures = get_course_lectures(course_id)

        return {
            "status": "success",
            "course_id": course_id,
            "total_lectures": len(lectures),
            "lectures": lectures
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Lecture listing error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve course lectures."
        )

# Semantic search across lecture materials

@app.post("/search")
def semantic_search_api(
    request: SemanticSearchRequest,
    student=Depends(require_student)
):
    try:
        if not request.query.strip():
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty."
            )

        if request.limit < 1 or request.limit > 20:
            raise HTTPException(
                status_code=400,
                detail="Limit must be between 1 and 20."
            )

        results = search_lectures(
            query=request.query,
            limit=request.limit
        )

        return {
            "status": "success",
            "query": request.query,
            "total_results": len(results),
            "results": results
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Semantic search error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to perform semantic search."
        )
