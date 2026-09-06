import joblib
import sys
import os
from urllib.parse import urlparse

# Make sure Python can find files inside src
sys.path.append(
    os.path.dirname(os.path.abspath(__file__))
)

from feature_extraction import extract_features
from risk_analysis import analyze_risk


# ==========================================
# LOAD MODEL
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "phishing_model.pkl"
)

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
vectorizer = model_data["vectorizer"]


# ==========================================
# TRUSTED DOMAINS
# ==========================================

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
}


# ==========================================
# CHECK TRUSTED DOMAIN
# ==========================================

def is_trusted_domain(url):
    """
    Check whether the URL belongs to a known
    trusted domain.
    """

    if "://" not in url:
        url = "https://" + url

    parsed = urlparse(url)

    domain = parsed.netloc.lower().split(":")[0]

    # Remove www.
    if domain.startswith("www."):
        domain = domain[4:]

    return domain in TRUSTED_DOMAINS


# ==========================================
# PREDICT URL
# ==========================================

def predict_url(url):
    """
    Analyze a URL using:

    1. Trusted domain verification
    2. Machine learning model
    3. Risk analysis

    Returns:
        result
        confidence
        risk_score
        reasons
    """

    # ======================================
    # EXTRACT FEATURES
    # ======================================

    features = extract_features(url)


    # ======================================
    # RISK ANALYSIS
    # ======================================

    risk_score, reasons = analyze_risk(
        url,
        features
    )


    # ======================================
    # TRUSTED DOMAIN CHECK
    # ======================================

    if is_trusted_domain(url):

        return (
            "LEGITIMATE",
            99.0,
            risk_score,
            reasons
        )


    # ======================================
    # MACHINE LEARNING
    # ======================================

    X = vectorizer.transform([url])

    prediction = model.predict(X)[0]

    probabilities = model.predict_proba(X)[0]

    confidence = max(probabilities) * 100


    # 0 = phishing
    # 1 = legitimate

    if prediction == 1:
        result = "LEGITIMATE"
    else:
        result = "PHISHING"


    # ======================================
    # RETURN RESULT
    # ======================================

    return (
        result,
        confidence,
        risk_score,
        reasons
    )