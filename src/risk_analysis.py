def analyze_risk(url, features):
    """
    Analyze URL features and generate
    a human-readable risk score.
    """

    risk_score = 0
    reasons = []

    url_lower = url.lower()

    # URL length
    if features["URLLength"] > 75:
        risk_score += 15
        reasons.append("URL is unusually long")

    # IP address
    if features["IsDomainIP"] == 1:
        risk_score += 25
        reasons.append("URL uses an IP address instead of a domain")

    # Subdomains
    if features["NoOfSubDomain"] >= 3:
        risk_score += 15
        reasons.append("URL contains many subdomains")

    # Hyphens
    hyphen_count = url.count("-")

    if hyphen_count >= 2:
        risk_score += 10
        reasons.append("URL contains multiple hyphens")

    # @ symbol
    if "@" in url:
        risk_score += 20
        reasons.append("URL contains an @ symbol")

    # Obfuscation
    if features["HasObfuscation"] == 1:
        risk_score += 15
        reasons.append("Possible URL obfuscation detected")

    # Suspicious keywords
    suspicious_keywords = [
        "login",
        "verify",
        "verification",
        "secure",
        "account",
        "update",
        "signin",
        "password",
        "confirm",
        "banking"
    ]

    detected_keywords = [
        word for word in suspicious_keywords
        if word in url_lower
    ]

    if detected_keywords:
        risk_score += min(len(detected_keywords) * 5, 20)
        reasons.append(
            "Suspicious keyword(s): "
            + ", ".join(detected_keywords)
        )

    # HTTPS
    if features["IsHTTPS"] == 0:
        risk_score += 10
        reasons.append("URL does not use HTTPS")

    # Cap score
    risk_score = min(risk_score, 100)

    return risk_score, reasons