import os
import re
import joblib


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "spam_model.pkl"
)


# ==========================================
# LOAD MODEL
# ==========================================

model_data = joblib.load(MODEL_PATH)

model = model_data["model"]
vectorizer = model_data["vectorizer"]


# ==========================================
# RISK ANALYSIS
# ==========================================

def analyze_message(message):

    text = message.lower()

    risk_score = 0
    reasons = []

    # --------------------------------------
    # Suspicious keywords
    # --------------------------------------

    keyword_groups = {
        "urgency": [
            "urgent",
            "immediately",
            "act now",
            "limited time",
            "hurry",
            "expires today",
            "last chance"
        ],

        "financial": [
            "bank",
            "payment",
            "money",
            "cash",
            "transfer",
            "credit card",
            "debit card",
            "account number"
        ],

        "credentials": [
            "password",
            "verify your account",
            "verification",
            "otp",
            "one time password",
            "pin",
            "login"
        ],

        "prize": [
            "you won",
            "winner",
            "congratulations",
            "lottery",
            "prize",
            "reward",
            "claim"
        ],

        "crypto": [
            "bitcoin",
            "crypto",
            "usdt",
            "ethereum",
            "wallet"
        ]
    }

    detected = []

    for category, keywords in keyword_groups.items():

        found = []

        for keyword in keywords:

            if keyword in text:
                found.append(keyword)

        if found:
            detected.extend(found)

    # --------------------------------------
    # Score based on keywords
    # --------------------------------------

    if detected:
        risk_score += min(len(detected) * 7, 35)

        reasons.append(
            "Suspicious keyword(s): "
            + ", ".join(detected[:6])
        )

    # --------------------------------------
    # URLs
    # --------------------------------------

    urls = re.findall(
        r"https?://\S+|www\.\S+",
        text
    )

    if urls:

        risk_score += 20

        reasons.append(
            "Message contains a link"
        )

        suspicious_domains = [
            "bit.ly",
            "tinyurl",
            "t.co",
            "goo.gl",
            "rb.gy",
            "is.gd"
        ]

        for url in urls:

            if any(
                domain in url.lower()
                for domain in suspicious_domains
            ):

                risk_score += 15

                reasons.append(
                    "Message contains a shortened URL"
                )

                break

    # --------------------------------------
    # Phone numbers
    # --------------------------------------

    phone_numbers = re.findall(
        r"(?:\+?\d[\d\s\-]{8,}\d)",
        text
    )

    if phone_numbers:

        risk_score += 10

        reasons.append(
            "Message contains a phone number"
        )

    # --------------------------------------
    # Money symbols
    # --------------------------------------

    if "$" in message or "£" in message or "€" in message:

        risk_score += 10

        reasons.append(
            "Message contains a monetary amount"
        )

    # --------------------------------------
    # Excessive punctuation
    # --------------------------------------

    if message.count("!") >= 3:

        risk_score += 5

        reasons.append(
            "Excessive use of exclamation marks"
        )

    # --------------------------------------
    # ALL CAPS
    # --------------------------------------

    words = message.split()

    if len(words) >= 5:

        uppercase_words = [
            word for word in words
            if word.isupper() and len(word) >= 3
        ]

        if len(uppercase_words) >= 3:

            risk_score += 5

            reasons.append(
                "Message contains excessive capitalization"
            )

    # --------------------------------------
    # Limit score
    # --------------------------------------

    risk_score = min(risk_score, 100)

    return risk_score, reasons


# ==========================================
# PREDICT MESSAGE
# ==========================================

def predict_message(message):

    if not message or not message.strip():

        return (
            "ERROR",
            0,
            0,
            ["Message cannot be empty."]
        )

    # --------------------------------------
    # ML prediction
    # --------------------------------------

    transformed = vectorizer.transform(
        [message]
    )

    prediction = model.predict(
        transformed
    )[0]

    probabilities = model.predict_proba(
        transformed
    )[0]

    confidence = max(probabilities) * 100

    # 0 = legitimate
    # 1 = spam

    if prediction == 1:

        result = "SPAM"

    else:

        result = "LEGITIMATE"

    # --------------------------------------
    # Risk analysis
    # --------------------------------------

    risk_score, reasons = analyze_message(
        message
    )

    # --------------------------------------
    # If ML says spam, ensure risk isn't 0
    # --------------------------------------

    if result == "SPAM" and risk_score < 25:

        risk_score = 25

    return (
        result,
        confidence,
        risk_score,
        reasons
    )