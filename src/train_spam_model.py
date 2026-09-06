import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "spam",
    "SMSSpamCollection"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "spam_model.pkl"
)


# ==========================================
# LOAD DATASET
# ==========================================

print("\n===================================")
print("       SPAM MODEL TRAINING")
print("===================================\n")

print("Loading dataset...")

df = pd.read_csv(
    DATASET_PATH,
    sep="\t",
    header=None,
    names=["label", "message"],
    encoding="utf-8"
)

print(f"Dataset loaded: {len(df):,} messages")


# ==========================================
# CLEAN DATA
# ==========================================

df = df.dropna()

df["label"] = df["label"].map({
    "ham": 0,
    "spam": 1
})

print("\nLabel distribution:")
print(df["label"].value_counts())

print("\nLabel meaning:")
print("0 = LEGITIMATE")
print("1 = SPAM")


# ==========================================
# DATA
# ==========================================

X = df["message"]
y = df["label"]


# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# TF-IDF
# ==========================================

print("\nCreating TF-IDF features...")

vectorizer = TfidfVectorizer(
    lowercase=True,
    strip_accents="unicode",
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.98,
    sublinear_tf=True
)

X_train_tfidf = vectorizer.fit_transform(X_train)
X_test_tfidf = vectorizer.transform(X_test)

print(
    "TF-IDF features created:",
    X_train_tfidf.shape[1]
)


# ==========================================
# MODEL
# ==========================================

print("\nTraining Logistic Regression...")

model = LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42
)

model.fit(
    X_train_tfidf,
    y_train
)

print("Training complete!")


# ==========================================
# EVALUATION
# ==========================================

print("\nEvaluating model...")

predictions = model.predict(X_test_tfidf)

accuracy = accuracy_score(
    y_test,
    predictions
)

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)

print("\n===== CLASSIFICATION REPORT =====")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Legitimate",
            "Spam"
        ]
    )
)

print("\n===== CONFUSION MATRIX =====")

print(
    confusion_matrix(
        y_test,
        predictions
    )
)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    {
        "model": model,
        "vectorizer": vectorizer
    },
    MODEL_PATH
)

print("\n===================================")
print("MODEL SAVED SUCCESSFULLY")
print("===================================")

print(
    f"\nSaved to:\n{MODEL_PATH}"
)