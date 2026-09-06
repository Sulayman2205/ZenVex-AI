import os
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# PATHS
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATASET_PATH = os.path.join(
    BASE_DIR,
    "dataset",
    "phiusiil+phishing+url+dataset (1)",
    "PhiUSIIL_Phishing_URL_Dataset.csv"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "phishing_model.pkl"
)


# ==========================================
# LOAD DATASET
# ==========================================

print("\n===================================")
print("     PHISHING URL MODEL TRAINING")
print("===================================\n")

print("Loading dataset...")

df = pd.read_csv(DATASET_PATH)

df = df[["URL", "label"]].dropna()

df["URL"] = df["URL"].astype(str)

print(f"Dataset loaded: {len(df):,} URLs")

print("\nLabel distribution:")
print(df["label"].value_counts().sort_index())

print("\nLabel meaning:")
print("0 = PHISHING")
print("1 = LEGITIMATE")


# ==========================================
# DATA
# ==========================================

X = df["URL"]
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
# TF-IDF URL VECTORIZER
# ==========================================

print("\nCreating character-level TF-IDF features...")

vectorizer = TfidfVectorizer(
    analyzer="char",
    ngram_range=(2, 5),
    min_df=2,
    max_features=150000,
    sublinear_tf=True
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

print(
    f"TF-IDF features created: "
    f"{X_train_vec.shape[1]:,}"
)


# ==========================================
# TRAIN MODEL
# ==========================================

print("\nTraining Logistic Regression...")

model = LogisticRegression(
    C=10,
    max_iter=1000,
    class_weight="balanced",
    solver="liblinear",
    random_state=42
)

model.fit(X_train_vec, y_train)

print("Training complete!")


# ==========================================
# EVALUATION
# ==========================================

print("\nEvaluating model...")

predictions = model.predict(X_test_vec)

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
            "Phishing",
            "Legitimate"
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