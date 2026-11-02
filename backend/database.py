
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def get_connection():
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            database=os.getenv("DB_NAME", "edustream_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432")
        )

        return connection

    except psycopg2.Error as error:
        print("Database connection failed:", error)
        return None


if __name__ == "__main__":
    connection = get_connection()

    if connection:
        print("Connected to EduStream database successfully!")
        connection.close()
