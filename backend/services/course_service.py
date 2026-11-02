
from database import get_connection


def get_course_by_code(course_code):
    """Retrieve a course using its unique course code."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Could not connect to PostgreSQL.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT course_id, course_code, course_name
            FROM courses
            WHERE UPPER(course_code) = UPPER(%s);
            """,
            (course_code.strip(),)
        )

        result = cursor.fetchone()

        if result is None:
            return None

        return {
            "course_id": result[0],
            "course_code": result[1],
            "course_name": result[2]
        }

    finally:
        connection.close()


def get_all_courses():
    """Retrieve all courses with instructor information."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                c.course_id,
                c.course_code,
                c.course_name,
                c.description,
                c.instructor_id,
                u.full_name AS instructor_name
            FROM courses c
            LEFT JOIN users u
                ON c.instructor_id = u.user_id
            ORDER BY c.course_id;
        """)

        rows = cursor.fetchall()

        return [
            {
                "course_id": row[0],
                "course_code": row[1],
                "course_name": row[2],
                "description": row[3],
                "instructor_id": row[4],
                "instructor_name": row[5]
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_course_by_id(course_id):
    """Retrieve a course using its ID."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                c.course_id,
                c.course_code,
                c.course_name,
                c.description,
                c.instructor_id,
                u.full_name AS instructor_name
            FROM courses c
            LEFT JOIN users u
                ON c.instructor_id = u.user_id
            WHERE c.course_id = %s;
        """, (course_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "course_id": row[0],
            "course_code": row[1],
            "course_name": row[2],
            "description": row[3],
            "instructor_id": row[4],
            "instructor_name": row[5]
        }

    finally:
        connection.close()


def create_course(course_code, course_name, description, instructor_id):
    """Create a course assigned to the authenticated instructor."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO courses
                (course_code, course_name, description, instructor_id)
            VALUES (%s, %s, %s, %s)
            RETURNING course_id, course_code, course_name,
                      description, instructor_id;
            """,
            (
                course_code.strip(),
                course_name.strip(),
                description,
                instructor_id
            )
        )

        row = cursor.fetchone()
        connection.commit()

        return {
            "course_id": row[0],
            "course_code": row[1],
            "course_name": row[2],
            "description": row[3],
            "instructor_id": row[4]
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def enroll_student(student_id, course_id):
    """Enroll a student in a course."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO enrollments (student_id, course_id)
            VALUES (%s, %s)
            ON CONFLICT (student_id, course_id) DO NOTHING
            RETURNING enrollment_id, student_id, course_id,
                      enrolled_at, status;
            """,
            (student_id, course_id)
        )

        row = cursor.fetchone()

        if row is None:
            connection.rollback()
            return None

        connection.commit()

        return {
            "enrollment_id": row[0],
            "student_id": row[1],
            "course_id": row[2],
            "enrolled_at": row[3],
            "status": row[4]
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_student_courses(student_id):
    """Retrieve all courses enrolled by a student."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                c.course_id,
                c.course_code,
                c.course_name,
                c.description,
                u.full_name AS instructor_name,
                e.enrollment_id,
                e.enrolled_at,
                e.status
            FROM enrollments e
            JOIN courses c
                ON e.course_id = c.course_id
            LEFT JOIN users u
                ON c.instructor_id = u.user_id
            WHERE e.student_id = %s
            ORDER BY e.enrolled_at DESC;
            """,
            (student_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "course_id": row[0],
                "course_code": row[1],
                "course_name": row[2],
                "description": row[3],
                "instructor_name": row[4],
                "enrollment_id": row[5],
                "enrolled_at": row[6],
                "status": row[7]
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_instructor_courses(instructor_id):
    """Retrieve all courses assigned to an instructor."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                course_id,
                course_code,
                course_name,
                description,
                instructor_id,
                created_at
            FROM courses
            WHERE instructor_id = %s
            ORDER BY created_at DESC;
            """,
            (instructor_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "course_id": row[0],
                "course_code": row[1],
                "course_name": row[2],
                "description": row[3],
                "instructor_id": row[4],
                "created_at": row[5]
            }
            for row in rows
        ]

    finally:
        connection.close()


def get_course_lectures(course_id):
    """Retrieve all lectures uploaded for a course."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                lecture_id,
                course_id,
                title,
                file_path,
                uploaded_at
            FROM lectures
            WHERE course_id = %s
            ORDER BY uploaded_at DESC;
            """,
            (course_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "lecture_id": row[0],
                "course_id": row[1],
                "title": row[2],
                "file_path": row[3],
                "uploaded_at": row[4]
            }
            for row in rows
        ]

    finally:
        connection.close()
