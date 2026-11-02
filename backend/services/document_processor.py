
from pypdf import PdfReader
from pptx import Presentation
import os


def extract_pdf_text(file_path):
    """Extract text from a PDF file."""
    text = []

    reader = PdfReader(file_path)

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text()

        if page_text:
            text.append(page_text)

    return "\n".join(text)


def extract_ppt_text(file_path):
    """Extract text from a PowerPoint presentation."""
    text = []

    presentation = Presentation(file_path)

    for slide_number, slide in enumerate(presentation.slides, start=1):
        for shape in slide.shapes:
            if hasattr(shape, "text") and shape.text.strip():
                text.append(shape.text)

    return "\n".join(text)


def extract_document_text(file_path):
    """Choose the extraction method based on file extension."""
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".pptx":
        return extract_ppt_text(file_path)

    else:
        raise ValueError("Only PDF and PPTX files are supported.")
