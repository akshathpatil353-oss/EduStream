from database import get_connection
from services.embedding_service import generate_embedding


def search_lectures(query, limit=5):
    """
    Find the most relevant lecture chunks for a student's question.
    Uses cosine distance through pgvector.
    """

    if not query or not query.strip():
        return []

    # 1. Convert the question into an embedding
    query_embedding = generate_embedding(query)

    # 2. Convert embedding into PostgreSQL vector format
    vector_value = "[" + ",".join(
        str(float(value)) for value in query_embedding
    ) + "]"

    # 3. Search PostgreSQL for the closest embeddings
    connection = get_connection()

    if connection is None:
        raise ConnectionError("Could not connect to PostgreSQL.")

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                l.title,
                lc.chunk_text,
                lc.chunk_index,
                le.embedding <=> %s::vector AS distance
            FROM lecture_embeddings le
            JOIN lecture_chunks lc
                ON le.chunk_id = lc.chunk_id
            JOIN lectures l
                ON lc.lecture_id = l.lecture_id
            ORDER BY le.embedding <=> %s::vector
            LIMIT %s;
            """,
            (vector_value, vector_value, limit)
        )

        results = cursor.fetchall()

        return [
            {
                "lecture_title": row[0],
                "chunk_text": row[1],
                "chunk_index": row[2],
                "similarity": round(1 - row[3], 4)
            }
            for row in results
        ]

    finally:
        connection.close()