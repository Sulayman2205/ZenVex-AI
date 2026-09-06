import pandas as pd


file_path = "dataset/phiusiil+phishing+url+dataset (1)/PhiUSIIL_Phishing_URL_Dataset.csv"


df = pd.read_csv(file_path)

print("\n===== DATASET INFORMATION =====")
print(f"Rows: {df.shape[0]}")
print(f"Columns: {df.shape[1]}")

print("\n===== COLUMN NAMES =====")
print(df.columns.tolist())

print("\n===== FIRST 5 ROWS =====")
print(df.head())

print("\n===== LABEL DISTRIBUTION =====")
print(df["label"].value_counts())

print("\n===== MISSING VALUES =====")
print(df.isnull().sum().sum())

print("\n===== LABEL MEANING =====")
print("Label 1 = Legitimate URL")
print("Label 0 = Phishing URL")