import joblib
import sys
import os
from urllib.parse import urlparse

sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from feature_extraction import extract_features
from risk_analysis import analyze_risk


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "phishing_model.pkl"
)

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
vectorizer = model_data["vectorizer"]


TRUSTED_DOMAINS = {
    "google.com",
    "openai.com",
    "apple.com",
    "amazon.com",
    "microsoft.com",
    "github.com",
    "youtube.com",
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "wikipedia.org",
    "example.com",
}


def normalize_url(url):

    url = url.strip()

    if not url:
        return ""

    if "://" not in url:
        url = "https://" + url

    return url


def get_domain(url):

    url = normalize_url(url)

    try:

        parsed = urlparse(url)

        domain = parsed.hostname

        if not domain:
            return ""

        domain = domain.lower().strip(".")

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:

        return ""


def is_trusted_domain(url):

    domain = get_domain(url)

    if not domain:
        return False

    return domain in TRUSTED_DOMAINS


def predict_url(url):

    url = normalize_url(url)

    if not url:
        raise ValueError(
            "URL cannot be empty."
        )

    domain = get_domain(url)

    if not domain:
        raise ValueError(
            "Unable to identify the domain."
        )

    features = extract_features(url)

    risk_score, reasons = analyze_risk(
        url,
        features
    )

    if is_trusted_domain(url):

        return (
            "LEGITIMATE",
            99.0,
            risk_score,
            reasons
        )

    X = vectorizer.transform([url])

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    confidence = max(probabilities) * 100

    if prediction == 1:

        result = "LEGITIMATE"

    else:

        result = "PHISHING"

    return (
        result,
        confidence,
        risk_score,
        reasons
    )