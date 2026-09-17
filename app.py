import os
import re
import tempfile

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from src.predict import predict_url
from src.spam_predict import predict_message
from src.pdf_qa import answer_pdf_question

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

MAX_PDF_SIZE = 5 * 1024 * 1024
MAX_URL_LENGTH = 2048
MAX_MESSAGE_LENGTH = 5000
MAX_QUESTION_LENGTH = 1000


def normalize_url(url):
    url = url.strip()

    if not url:
        return ""

    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "https://" + url

    return url


def is_valid_url(url):
    url = normalize_url(url)

    if not url:
        return False

    if len(url) > MAX_URL_LENGTH:
        return False

    if " " in url:
        return False

    try:
        from urllib.parse import urlparse

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            return False

        if not parsed.netloc:
            return False

        domain = parsed.hostname

        if not domain:
            return False

        domain = domain.lower().strip(".")

        if ".." in domain:
            return False

        if domain == "localhost":
            return False

        if re.match(r"^\d+\.\d+\.\d+\.\d+$", domain):
            return True

        if "." not in domain:
            return False

        parts = domain.split(".")

        if any(not part for part in parts):
            return False

        if any(
            not re.match(r"^[a-zA-Z0-9-]+$", part)
            for part in parts
        ):
            return False

        if len(parts[-1]) < 2:
            return False

        return True

    except Exception:
        return False


def is_pdf(file):
    if not file:
        return False

    filename = secure_filename(file.filename)

    return filename.lower().endswith(".pdf")


def save_uploaded_pdf(file):
    if not file or not file.filename:
        return None

    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_PDF_SIZE:
        raise ValueError("PDF file is too large. Maximum allowed size is 5 MB.")

    if not is_pdf(file):
        raise ValueError("Please upload a valid PDF file.")

    filename = secure_filename(file.filename)

    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, filename)

    file.save(temp_path)

    return temp_path


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/phishing", methods=["GET", "POST"])
def phishing():
    result = None
    confidence = None
    risk_score = None
    reasons = []
    url = ""

    if request.method == "POST":
        url = request.form.get("url", "").strip()
        normalized_url = normalize_url(url)

        if not url:
            result = "ERROR"
            reasons = [
                "Please enter a URL."
            ]

        elif len(url) > MAX_URL_LENGTH:
            result = "ERROR"
            reasons = [
                "The URL is too long. Maximum allowed length is 2048 characters."
            ]
            print("PHISHING ERROR: URL exceeds maximum length.")

        elif not is_valid_url(url):
            result = "ERROR"
            reasons = [
                "Please enter a complete and valid URL.",
                "Example: https://example.com"
            ]
            print("PHISHING ERROR: Invalid URL format.")

        else:
            url = normalized_url

            try:
                result, confidence, risk_score, reasons = predict_url(url)

            except Exception as e:
                print("PHISHING ERROR:", e)

                result = "ERROR"
                reasons = [
                    "Unable to analyze this URL.",
                    "Please check that the URL is complete and try again."
                ]

    return render_template(
        "phishing.html",
        result=result,
        confidence=confidence,
        risk_score=risk_score,
        reasons=reasons,
        url=url
    )


@app.route("/spam", methods=["GET", "POST"])
def spam():
    result = None
    confidence = None
    risk_score = None
    reasons = []
    message = ""

    if request.method == "POST":
        message = request.form.get("message", "").strip()

        if not message:
            result = "ERROR"
            reasons = [
                "Please enter a message."
            ]

        elif len(message) > MAX_MESSAGE_LENGTH:
            result = "ERROR"
            reasons = [
                "The message is too long. Maximum allowed length is 5000 characters."
            ]

        else:
            try:
                result, confidence, risk_score, reasons = predict_message(
                    message
                )

            except Exception as e:
                print("SPAM ERROR:", e)

                result = "ERROR"
                reasons = [
                    "Unable to analyze this message.",
                    "Please try again."
                ]

    return render_template(
        "spam.html",
        result=result,
        confidence=confidence,
        risk_score=risk_score,
        reasons=reasons,
        message=message
    )


@app.route("/resume", methods=["GET", "POST"])
def resume():
    result = None
    error = None
    filename = None

    if request.method == "POST":
        file = request.files.get("resume")

        if not file or not file.filename:
            error = "Please upload a resume PDF."

        else:
            filename = secure_filename(file.filename)

            if not filename.lower().endswith(".pdf"):
                error = "Please upload a PDF file."

            else:
                try:
                    from src.resume_pdf import extract_resume_text
                    from src.resume_analyzer import analyze_resume

                    temp_path = save_uploaded_pdf(file)

                    text = extract_resume_text(temp_path)

                    if not text.strip():
                        raise ValueError(
                            "Could not extract readable text from the PDF."
                        )

                    result = analyze_resume(text)

                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass

                except Exception as e:
                    print("RESUME ERROR:", e)
                    error = (
                        "Unable to analyze the resume. "
                        "Please make sure the PDF contains readable text."
                    )

    return render_template(
        "resume.html",
        result=result,
        error=error,
        filename=filename
    )


@app.route("/pdf-qa", methods=["GET", "POST"])
def pdf_qa():
    answer = None
    error = None
    filename = None
    question = ""

    if request.method == "POST":
        file = request.files.get("pdf")
        question = request.form.get("question", "").strip()

        if not file or not file.filename:
            error = "Please upload a PDF file."

        elif not question:
            error = "Please enter a question."

        elif len(question) > MAX_QUESTION_LENGTH:
            error = "The question is too long. Maximum allowed length is 1000 characters."

        else:
            filename = secure_filename(file.filename)

            try:
                temp_path = save_uploaded_pdf(file)

                answer = answer_pdf_question(
                    temp_path,
                    question
                )

                try:
                    os.remove(temp_path)
                except Exception:
                    pass

            except Exception as e:
                print("PDF Q&A ERROR:", e)

                error = (
                    "Unable to process the PDF. "
                    "Please make sure the file is valid and try again."
                )

    return render_template(
        "pdf_qa.html",
        answer=answer,
        error=error,
        filename=filename,
        question=question
    )


@app.errorhandler(413)
def request_entity_too_large(error):
    return render_template(
        "error.html",
        error="The uploaded file is too large."
    ), 413


if __name__ == "__main__":
    app.run(debug=False)