import pandas as pd
import os

# Define the required columns (matching raw data)
important_columns = [
    "Dst Port", "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts",
    "Flow Byts/s", "Flow Pkts/s", "Pkt Len Max", "Pkt Len Mean", "Pkt Len Std",
    "SYN Flag Cnt", "ACK Flag Cnt", "FIN Flag Cnt", "Label"
]

# Path to dataset folder
dataset_folder = "CIC-IDS2018"

# List all CSV files in dataset folder
files = [f for f in os.listdir(dataset_folder) if f.endswith(".csv")]

# Merge all datasets
merged_df = pd.DataFrame()

for file in files:
    file_path = os.path.join(dataset_folder, file)
    print(f"Processing: {file_path}")
    
    df = pd.read_csv(file_path, usecols=lambda column: column in important_columns, low_memory=False)
    
    merged_df = pd.concat([merged_df, df], ignore_index=True)

# Save merged dataset
merged_df.to_csv("merged_data.csv", index=False)
print("✅ Merging completed! Saved as 'merged_data.csv'")
