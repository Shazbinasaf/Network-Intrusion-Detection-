import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler
from sklearn.inspection import permutation_importance
import os

# 📌 Load dataset
DATA_PATH = "balanced_data.csv"
MODEL_PATH = "backend/model.pkl"
SCALER_PATH = "scaler.pkl"
FEATURE_IMPORTANCE_PLOT = "feature_importance_plot.png"
FEATURE_IMPORTANCE_REPORT = "feature_importance_report.txt"
CLASSIFICATION_REPORT = "classification_report.txt"

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"❌ Dataset not found: {DATA_PATH}")

print("📌 Loading preprocessed dataset...")
df = pd.read_csv(DATA_PATH)
print(f"✅ Dataset Loaded! Total records: {len(df)}")

# ✅ Verify Label Distribution
print("📌 Checking label distribution...")
print(df["Label"].value_counts())

# ✅ Select important features
important_features = [
    "Dst Port", "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts",
    "Flow Byts/s", "Flow Pkts/s", "Pkt Len Max", "Pkt Len Mean", 
    "Pkt Len Std", "SYN Flag Cnt", "ACK Flag Cnt", "FIN Flag Cnt"
]

# ✅ Ensure all important features exist in dataset
for feature in important_features:
    if feature not in df.columns:
        raise ValueError(f"❌ Missing feature in dataset: {feature}")

X = df[important_features]
y = df["Label"]

# ✅ Feature Scaling
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ✅ Save scaler for later use in API
joblib.dump(scaler, SCALER_PATH)

# ✅ Split into training and testing sets
print("📌 Splitting data into training (80%) and testing (20%) sets...")
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)
print(f"✅ Data split completed! Training size: {len(X_train)}, Testing size: {len(X_test)}")

# ✅ Dynamically Adjust `scale_pos_weight`
normal_count = np.sum(y_train == 0)
malicious_count = np.sum(y_train == 1)
if malicious_count == 0:
    raise ValueError("❌ Malicious class has zero instances in training data! Adjust dataset.")

scale_pos_weight = (normal_count / malicious_count) * 1.5  # Adjusting weight dynamically
print(f"📌 Adjusted scale_pos_weight: {scale_pos_weight:.2f}")

# ✅ Train XGBoost Classifier
print("📌 Training XGBoost Classifier...")
model = XGBClassifier(
    n_estimators=300,  # Increased for better learning
    learning_rate=0.1,
    max_depth=8,  # Deeper trees for better feature extraction
    scale_pos_weight=scale_pos_weight,  # Adjusted weight for malicious class
    eval_metric="logloss",
    random_state=42
)

model.fit(X_train, y_train)
print("✅ Model training completed!")

# ✅ Test Model
print("📌 Testing model on test data...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"🎯 Model Accuracy: {accuracy * 100:.2f}%")

# ✅ Generate Classification Report
print("📌 Generating Model Performance Report...")
report = classification_report(y_test, y_pred, target_names=["Normal", "Malicious"])
print(report)

# ✅ Save Report to File
with open(CLASSIFICATION_REPORT, "w") as f:
    f.write(report)
print(f"✅ Classification Report saved as '{CLASSIFICATION_REPORT}'")

# ✅ Explainable AI: Feature Importance using Permutation Importance
print("📌 Calculating Feature Importance using Permutation Importance...")
X_sample = X_test[:10000]
y_sample = y_test.iloc[:10000]
perm_importance = permutation_importance(model, X_sample, y_sample, scoring="accuracy", random_state=42)

# ✅ Save Feature Importance Report
with open(FEATURE_IMPORTANCE_REPORT, "w") as f:
    for i, feature in enumerate(important_features):
        f.write(f"{feature}: {perm_importance.importances_mean[i]:.6f}\n")
print(f"✅ Feature Importance saved as '{FEATURE_IMPORTANCE_REPORT}'")

# ✅ Plot Feature Importance
print("📌 Plotting Feature Importance...")
sorted_idx = np.argsort(perm_importance.importances_mean)
plt.figure(figsize=(10, 6))
plt.barh([important_features[i] for i in sorted_idx], perm_importance.importances_mean[sorted_idx], color="skyblue")
plt.xlabel("Feature Importance Score")
plt.ylabel("Features")
plt.title("Feature Importance (Permutation Importance)")
plt.savefig(FEATURE_IMPORTANCE_PLOT)
plt.show()
print(f"✅ Feature importance plot saved as '{FEATURE_IMPORTANCE_PLOT}'")

# ✅ Save the trained model
joblib.dump(model, MODEL_PATH)
print(f"✅ Model saved as '{MODEL_PATH}'")
# ✅ Save Training Data for SHAP Background Sampling
X_train_sample = X_train[:1000]  # Save the first 1000 rows
joblib.dump(X_train_sample, "X_train_sample.pkl")
print("✅ Saved a sample of training data for SHAP.")
