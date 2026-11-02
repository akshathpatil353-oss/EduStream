
from sentence_transformers import SentenceTransformer

# Load the embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text):
    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


def generate_embeddings(chunks):
    embeddings = model.encode(
        chunks,
        normalize_embeddings=True
    )

    return embeddings.tolist()
