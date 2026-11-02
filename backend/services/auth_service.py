
import psycopg2

from database import get_connection
from services.password_service import hash_password, verify_password


def register_user(full_name, email, password, role):
    """Register a new student or instructor."""

    if role not in ("student", "instructor"):
        raise ValueError("Invalid role.")

    if not full_name.strip() or not email.strip():
        raise ValueError("Name and email are required.")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters.")

    password_hash = hash_password(password)

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash, role)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id, full_name, email, role;
            """,
            (full_name.strip(), email.strip().lower(), password_hash, role)
        )

        user = cursor.fetchone()
        connection.commit()

        return {
            "user_id": user[0],
            "full_name": user[1],
            "email": user[2],
            "role": user[3]
        }

    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        raise ValueError("An account with this email already exists.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def login_user(email, password):
    """Authenticate a user using email and password."""

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Database connection failed.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT user_id, full_name, email, password_hash, role
            FROM users
            WHERE email = %s;
            """,
            (email.strip().lower(),)
        )

        user = cursor.fetchone()

        if user is None:
            return None

        if not verify_password(password, user[3]):
            return None

        return {
            "user_id": user[0],
            "full_name": user[1],
            "email": user[2],
            "role": user[4]
        }




    finally:
        connection.close()
