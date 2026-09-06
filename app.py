import os
import re
import tempfile

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from src.predict import predict_url
from src.spam_predict import predict_message
from src.pdf_qa import answer_pdf_question


app = Flask(__name__)


# ==========================================
# APPLICATION SETTINGS
# ==========================================

# Maximum total request size: 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# Maximum PDF size: 5 MB
MAX_PDF_SIZE = 5 * 1024 * 1024

# Maximum URL length
MAX_URL_LENGTH = 2048

# Maximum message length
MAX_MESSAGE_LENGTH = 5000

# Maximum PDF question length
MAX_QUESTION_LENGTH = 1000


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def is_valid_url(url):
    """
    Basic URL validation.

    Requires:
    - http:// or https://
    - a valid-looking domain
    """

    pattern = re.compile(
        r"^https?://"
        r"(?=.{1,253}$)"
        r"(?:[a-zA-Z0-9-]+\.)+"
        r"[a-zA-Z]{2,}"
        r"(?::\d+)?"
        r"(?:[/?#][^\s]*)?$"
    )

    return bool(pattern.match(url))


def is_pdf(file):
    """
    Validate that the uploaded file appears to be a PDF.
    """

    if not file or not file.filename:
        return False

    filename = secure_filename(file.filename)

    return filename.lower().endswith(".pdf")


def save_uploaded_pdf(file):
    """
    Safely save an uploaded PDF to a temporary file.

    Returns:
        temp_path
    """

    if not file or not file.filename:
        raise ValueError("No file was uploaded.")

    if not is_pdf(file):
        raise ValueError("Only PDF files are supported.")

    filename = secure_filename(file.filename)

    if not filename.lower().endswith(".pdf"):
        raise ValueError("Only PDF files are supported.")

    # Read file into memory only for size checking.
    # 5 MB is small enough for this application.
    file_data = file.read()

    if len(file_data) > MAX_PDF_SIZE:
        raise ValueError(
            "PDF file is too large. Maximum allowed size is 5 MB."
        )

    if len(file_data) == 0:
        raise ValueError("The uploaded PDF is empty.")

    # Basic PDF signature check
    if not file_data.startswith(b"%PDF"):
        raise ValueError(
            "The uploaded file does not appear to be a valid PDF."
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp:

            temp.write(file_data)
            temp_path = temp.name

        return temp_path

    except Exception:

        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        raise


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# PHISHING URL DETECTOR
# ==========================================

@app.route("/phishing", methods=["GET", "POST"])
def phishing():

    result = None
    confidence = None
    risk_score = None
    reasons = []
    url = ""

    if request.method == "POST":

        url = request.form.get("url", "").strip()

        # Empty URL
        if not url:

            result = "ERROR"

        # URL too long
        elif len(url) > MAX_URL_LENGTH:

            result = "ERROR"

            print("PHISHING ERROR: URL exceeds maximum length.")

        # Invalid URL format
        elif not is_valid_url(url):

            result = "ERROR"

            print("PHISHING ERROR: Invalid URL format.")

        else:

            try:

                result, confidence, risk_score, reasons = predict_url(url)

            except Exception as e:

                print("PHISHING ERROR:", e)

                result = "ERROR"

    return render_template(
        "phishing.html",
        result=result,
        confidence=confidence,
        risk_score=risk_score,
        reasons=reasons,
        url=url
    )


# ==========================================
# SPAM / FRAUD DETECTOR
# ==========================================

@app.route("/spam", methods=["GET", "POST"])
def spam():

    result = None
    confidence = None
    risk_score = None
    reasons = []
    message = ""

    if request.method == "POST":

        message = request.form.get(
            "message",
            ""
        ).strip()

        # Empty message
        if not message:

            result = "ERROR"

            print("SPAM ERROR: Empty message.")

        # Message too long
        elif len(message) > MAX_MESSAGE_LENGTH:

            result = "ERROR"

            print(
                "SPAM ERROR: Message exceeds maximum length."
            )

            message = message[:MAX_MESSAGE_LENGTH]

        else:

            try:

                result, confidence, risk_score, reasons = predict_message(
                    message
                )

            except Exception as e:

                print("SPAM ERROR:", e)

                result = "ERROR"

    return render_template(
        "spam.html",
        result=result,
        confidence=confidence,
        risk_score=risk_score,
        reasons=reasons,
        message=message
    )


# ==========================================
# RESUME ANALYZER
# ==========================================

@app.route("/resume", methods=["GET", "POST"])
def resume():

    result = None
    error = None

    if request.method == "POST":

        file = request.files.get("resume")

        if not file or not file.filename:

            error = "Please select a PDF resume."

        elif not is_pdf(file):

            error = "Only PDF files are supported."

        else:

            temp_path = None

            try:

                temp_path = save_uploaded_pdf(file)

                from src.resume_pdf import analyze_resume_pdf

                result = analyze_resume_pdf(temp_path)

            except ValueError as e:

                error = str(e)

                print("RESUME VALIDATION ERROR:", e)

            except Exception as e:

                print("RESUME ERROR:", e)

                error = (
                    "Unable to analyze this PDF. "
                    "Please make sure the file is a valid resume PDF."
                )

            finally:

                if temp_path and os.path.exists(temp_path):

                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        print(
                            "RESUME TEMP FILE CLEANUP ERROR:",
                            e
                        )

    return render_template(
        "resume.html",
        result=result,
        error=error
    )


# ==========================================
# PDF Q&A
# ==========================================

@app.route("/pdf-qa", methods=["GET", "POST"])
def pdf_qa():

    answer = None
    error = None
    question = ""

    if request.method == "POST":

        file = request.files.get("pdf")

        question = request.form.get(
            "question",
            ""
        ).strip()

        # Validate PDF
        if not file or not file.filename:

            error = "Please select a PDF file."

        elif not is_pdf(file):

            error = "Only PDF files are supported."

        # Validate question
        elif not question:

            error = "Please enter a question."

        elif len(question) > MAX_QUESTION_LENGTH:

            error = (
                "Question is too long. "
                "Please keep it under 1000 characters."
            )

        else:

            temp_path = None

            try:

                temp_path = save_uploaded_pdf(file)

                answer = answer_pdf_question(
                    temp_path,
                    question
                )

            except ValueError as e:

                error = str(e)

                print("PDF Q&A VALIDATION ERROR:", e)

            except Exception as e:

                print("PDF Q&A ERROR:", e)

                error = (
                    "Unable to answer the question from this PDF. "
                    "Please make sure the document is readable."
                )

            finally:

                if temp_path and os.path.exists(temp_path):

                    try:
                        os.remove(temp_path)
                    except Exception as e:
                        print(
                            "PDF TEMP FILE CLEANUP ERROR:",
                            e
                        )

    return render_template(
        "pdf_qa.html",
        answer=answer,
        error=error,
        question=question
    )


# ==========================================
# FILE SIZE ERROR
# ==========================================

@app.errorhandler(413)
def request_too_large(error):

    return render_template(
        "error.html",
        message=(
            "The uploaded file is too large. "
            "Please upload a file smaller than 10 MB."
        )
    ), 413


# ==========================================
# RUN SERVER
# ==========================================

if __name__ == "__main__":
    app.run(
        debug=False
    )