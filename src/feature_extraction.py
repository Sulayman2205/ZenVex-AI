import re
from urllib.parse import urlparse


def extract_features(url):
    """
    Extract numerical features from a URL.
    These features can be calculated using only the URL itself.
    """

    parsed = urlparse(url)

    domain = parsed.netloc
    path = parsed.path
    query = parsed.query

    features = {
        "URLLength": len(url),

        "DomainLength": len(domain),

        "IsDomainIP": int(
            bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", domain))
        ),

        "NoOfSubDomain": max(1, domain.count(".")),

        "NoOfLettersInURL": sum(c.isalpha() for c in url),

        "NoOfDegitsInURL": sum(c.isdigit() for c in url),

        "NoOfEqualsInURL": url.count("="),

        "NoOfQMarkInURL": url.count("?"),

        "NoOfAmpersandInURL": url.count("&"),

        "NoOfOtherSpecialCharsInURL": sum(
            not c.isalnum() and c not in ".-_/?:=&"
            for c in url
        ),

        "IsHTTPS": int(parsed.scheme.lower() == "https"),

        "HasObfuscation": int(
            "@" in url or
            "%" in url or
            "//" in path
        ),

        "NoOfObfuscatedChar": url.count("%"),

        "NoOfPopup": 0,

        "HasExternalFormSubmit": 0,

        "HasPasswordField": int(
            "password" in url.lower() or
            "passwd" in url.lower()
        ),

        "Bank": int("bank" in url.lower()),

        "Pay": int(
            any(word in url.lower() for word in [
                "paypal",
                "payment",
                "pay",
                "checkout"
            ])
        ),

        "Crypto": int(
            any(word in url.lower() for word in [
                "bitcoin",
                "crypto",
                "ethereum",
                "wallet"
            ])
        ),
    }

    return features


if __name__ == "__main__":

    test_url = "https://secure-paypal-login.com/account/verify?id=123"

    features = extract_features(test_url)

    print("\n===== URL FEATURE EXTRACTION =====")

    for feature, value in features.items():
        print(f"{feature}: {value}")