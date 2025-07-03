import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler

# ✅ Step 1: Load Dataset
print("📌 Loading merged dataset for preprocessing...")
df = pd.read_csv("merged_data.csv", low_memory=False)  # Ensure correct data loading
print(f"✅ Dataset Loaded! Total records: {len(df)}")

# ✅ Step 2: Convert Columns to Numeric (Fix Object Errors)
print("📌 Converting numeric columns while keeping non-numeric data intact...")
for col in df.columns:
    if col != "Label":  # Convert everything EXCEPT the Label column
        df[col] = pd.to_numeric(df[col], errors="coerce")

# ✅ Step 3: Convert Label Column to Numeric
print("📌 Checking Label column unique values...")
print(df["Label"].unique())  # Print unique label values

# Map 'Benign' → 0 and all attack types → 1
attack_labels = [
    "FTP-BruteForce", "SSH-Bruteforce", "DoS attacks-GoldenEye", "DoS attacks-Slowloris",
    "DoS attacks-SlowHTTPTest", "DoS attacks-Hulk", "DDoS attacks-LOIC-HTTP", "DDOS attack-LOIC-UDP",
    "DDOS attack-HOIC", "Brute Force -Web", "Brute Force -XSS", "SQL Injection", "Infilteration", "Bot"
]

df["Label"] = df["Label"].apply(lambda x: 0 if x == "Benign" else (1 if x in attack_labels else np.nan))
df.dropna(subset=["Label"], inplace=True)  # Remove any remaining NaN labels

print(f"✅ Updated Label Distribution:\n{df['Label'].value_counts()}")

# ✅ Step 4: Handle Missing Values (Fix SMOTE Issue)
print("📌 Checking for missing values in dataset...")
missing_values = df.isnull().sum().sum()
if missing_values > 0:
    print(f"⚠ Found {missing_values} missing values. Filling NaNs with column mean...")
    df.fillna(df.mean(), inplace=True)  # Replace NaN with column means
print("✅ Missing values handled.")

# ✅ Step 5: Handle Infinite (`inf`) or Very Large Values
print("📌 Checking for infinite values in dataset...")
df.replace([np.inf, -np.inf], np.nan, inplace=True)  # Convert inf to NaN
df.fillna(df.mean(), inplace=True)  # Replace NaN with column means

# Check if any inf values remain
if np.isinf(df).values.any():
    print("❌ ERROR: Infinite values still present! Stopping execution.")
    exit()
else:
    print("✅ Infinite values handled.")

# ✅ Step 6: Balance Dataset (Fix Bias Dynamically)
normal_count = len(df[df["Label"] == 0])
malicious_count = len(df[df["Label"] == 1])

print(f"📌 Normal samples: {normal_count}, Malicious samples: {malicious_count}")

# Apply SMOTE if imbalance is detected
if normal_count > 2 * malicious_count:
    print("⚠ Detected Imbalance! Applying SMOTE to balance the dataset...")

    # First, downsample Normal samples to 5 million for faster SMOTE
    rus = RandomUnderSampler(sampling_strategy=0.4, random_state=42)  # Reduce to 40% of normal
    X_downsampled, y_downsampled = rus.fit_resample(df.drop(columns=["Label"]), df["Label"])
    df_downsampled = pd.DataFrame(X_downsampled, columns=df.columns[:-1])
    df_downsampled["Label"] = y_downsampled

    # Apply SMOTE on the downsampled dataset
    print("⚠ Applying SMOTE on the reduced dataset for faster processing...")
    smote = SMOTE(sampling_strategy=1.0, random_state=42)
    X_resampled, y_resampled = smote.fit_resample(df_downsampled.drop(columns=["Label"]), df_downsampled["Label"])
    df_balanced = pd.DataFrame(X_resampled, columns=df.columns[:-1])
    df_balanced["Label"] = y_resampled

    print(f"✅ SMOTE applied! Balanced dataset size: {len(df_balanced)}")
else:
    print("✅ No severe imbalance detected. Proceeding with existing data.")
    df_balanced = df

# ✅ Step 7: Save Processed Data
df_balanced.to_csv("balanced_data.csv", index=False)
print("🎯 Preprocessing complete! Saved as 'balanced_data.csv'")
