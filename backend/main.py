
from pathlib import Path

from services.document_processor import extract_document_text
from services.text_chunker import split_text_into_chunks
from services.embedding_service import generate_embeddings
from services.storage_service import save_lecture_data
from services.course_service import get_course_by_code


def process_and_store_lecture(file_path, course_id):
    file_path = Path(file_path)

    if not file_path.exists():
        print("Error: File not found:", file_path)
        return

    print("\n1. Extracting document text...")
    text = extract_document_text(str(file_path))

    if not text.strip():
        print("No text found in the document.")
        return

    print("Extracted characters:", len(text))

    print("\n2. Splitting text into chunks...")
    chunks = split_text_into_chunks(
        text,
        chunk_size=500,
        overlap=100
    )

    print("Total chunks:", len(chunks))

    if not chunks:
        print("No chunks generated.")
        return

    print("\n3. Generating embeddings...")
    embeddings = generate_embeddings(chunks)

    print("Embeddings generated:", len(embeddings))
    print("Dimensions per embedding:", len(embeddings[0]))

    print("\n4. Saving data to PostgreSQL...")

    lecture_id = save_lecture_data(
        title=file_path.stem,
        file_path=str(file_path),
        course_id=course_id,
        chunks=chunks,
        embeddings=embeddings
    )

    print("\nLecture processing completed!")
    print("Saved lecture ID:", lecture_id)


if __name__ == "__main__":
    print("===== EduStream Lecture Upload =====")

    course_code = input("Enter course code: ").strip()

    course = get_course_by_code(course_code)

    if course is None:
        print("Error: Course not found. Please check the course code.")
    else:
        print("\nCourse found!")
        print("Course:", course["course_name"])
        print("Course code:", course["course_code"])
        print("Course ID:", course["course_id"])

        file_path = input(
            "\nEnter lecture PDF/PPTX path: "
        ).strip().strip('"')

        process_and_store_lecture(
            file_path,
            course["course_id"]
        )
