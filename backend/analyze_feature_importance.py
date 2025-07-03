import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.inspection import permutation_importance

# Load trained model
MODEL_PATH = "model.pkl"
model = joblib.load(MODEL_PATH)

# Load dataset for feature importance analysis
df = pd.read_csv("../cleaned_data.csv")  # Adjust path if needed
important_features = [
    "Dst Port", "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts",
    "Flow Byts/s", "Flow Pkts/s", "Pkt Len Max", "Pkt Len Mean", "Pkt Len Std",
    "SYN Flag Cnt", "ACK Flag Cnt", "FIN Flag Cnt"
]

# Use a small sample for fast computation
df_sample = df.sample(n=10000, random_state=42)

# Split into features and labels
X_sample = df_sample[important_features]
y_sample = df_sample["Label"]

# Compute Permutation Importance
print("📌 Calculating feature importance...")
perm_importance = permutation_importance(model, X_sample, y_sample, scoring="accuracy", random_state=42)

# Save Feature Importance Report
with open("feature_importance_report.txt", "w") as f:
    for i, feature in enumerate(important_features):
        f.write(f"{feature}: {perm_importance.importances_mean[i]:.6f}\n")

print("✅ Feature Importance saved as 'feature_importance_report.txt'")

# Plot Feature Importance
print("📌 Plotting Feature Importance...")
sorted_idx = np.argsort(perm_importance.importances_mean)
plt.figure(figsize=(8, 6))
plt.barh([important_features[i] for i in sorted_idx], perm_importance.importances_mean[sorted_idx], color="skyblue")
plt.xlabel("Feature Importance Score")
plt.ylabel("Features")
plt.title("Feature Importance (Permutation Importance)")
plt.savefig("feature_importance_plot.png")
print("✅ Feature importance plot saved as 'feature_importance_plot.png'")
