import os
from pypdf import PdfReader

from resume_analyzer import analyze_resume


def extract_resume_text(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def analyze_resume_pdf(file_path):

    text = extract_resume_text(file_path)

    result = analyze_resume(text)

    result["text"] = text

    return result