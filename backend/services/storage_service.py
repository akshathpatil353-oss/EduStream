
from database import get_connection


def save_lecture_data(title, file_path, course_id, chunks, embeddings):
    """Save lecture details, text chunks, and embeddings in PostgreSQL."""

    if len(chunks) != len(embeddings):
        raise ValueError("Number of chunks and embeddings must match.")

    connection = get_connection()

    if connection is None:
        raise ConnectionError("Could not connect to PostgreSQL.")

    try:
        cursor = connection.cursor()

        # 1. Insert lecture details
        cursor.execute(
            """
            INSERT INTO lectures (course_id, title, file_path)
            VALUES (%s, %s, %s)
            RETURNING lecture_id;
            """,
            (course_id, title, file_path)
        )

        lecture_id = cursor.fetchone()[0]

        # 2. Insert chunks and their embeddings
        for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):

            if len(embedding) != 384:
                raise ValueError(
                    f"Embedding {index} has {len(embedding)} dimensions, not 384."
                )

            cursor.execute(
                """
                INSERT INTO lecture_chunks
                    (lecture_id, chunk_text, chunk_index)
                VALUES (%s, %s, %s)
                RETURNING chunk_id;
                """,
                (lecture_id, chunk, index)
            )

            chunk_id = cursor.fetchone()[0]

            # Convert Python list into pgvector input format
            vector_value = "[" + ",".join(
                str(float(value)) for value in embedding
            ) + "]"

            cursor.execute(
                """
                INSERT INTO lecture_embeddings (chunk_id, embedding)
                VALUES (%s, %s::vector);
                """,
                (chunk_id, vector_value)
            )

        connection.commit()

        print("Lecture saved successfully!")
        print("Lecture ID:", lecture_id)
        print("Chunks saved:", len(chunks))
        print("Embeddings saved:", len(embeddings))

        return lecture_id

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
