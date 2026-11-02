
import re


def split_text_into_chunks(text, chunk_size=500, overlap=100):
    """
    Split lecture text into overlapping chunks.
    Chunk size and overlap are measured in words.
    """

    if not text or not text.strip():
        return []

    # Normalize unnecessary whitespace
    text = re.sub(r"\s+", " ", text).strip()

    words = text.split()

    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        if end == len(words):
            break

        start = end - overlap

    return chunks
