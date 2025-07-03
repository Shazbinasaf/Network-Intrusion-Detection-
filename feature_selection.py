import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.feature_selection import RFE
from sklearn.metrics import accuracy_score

# Load dataset (replace with actual dataset path)
df = pd.read_csv("balanced_data.csv")  # Ensure target column is labeled correctly

# Define features and target
X = df.drop(columns=['Attack_Type'])  
y = df['Attack_Type']  


# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForest classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Compute Permutation Importance
perm_importance = permutation_importance(model, X_test, y_test, n_repeats=10, random_state=42)
feature_importance = pd.Series(perm_importance.importances_mean, index=X.columns)
feature_importance.sort_values(ascending=False, inplace=True)

# Plot Feature Importance
plt.figure(figsize=(10, 5))
feature_importance.plot(kind="bar", color="skyblue")
plt.xlabel("Feature")
plt.ylabel("Importance Score")
plt.title("Feature Importance (Permutation)")
plt.xticks(rotation=45)
plt.show()

# Recursive Feature Elimination (RFE)
rfe = RFE(model, n_features_to_select=5)  # Select top 5 features
rfe.fit(X_train, y_train)

# Get selected features
selected_features = X.columns[rfe.support_]
print("Selected Features:", list(selected_features))

# Retrain model with selected features
X_train_rfe = X_train[selected_features]
X_test_rfe = X_test[selected_features]
model.fit(X_train_rfe, y_train)

# Evaluate new model
y_pred = model.predict(X_test_rfe)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy after Feature Selection: {accuracy:.4f}")
