from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import joblib
import os
import shap
import numpy as np
from sklearn.preprocessing import StandardScaler
import time

# ✅ Load model, scaler, and sample training data
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")
X_TRAIN_PATH = os.path.join(os.path.dirname(__file__), "X_train_sample.pkl")


if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH) or not os.path.exists(X_TRAIN_PATH):
    raise FileNotFoundError("❌ Model, scaler, or X_train_sample file is missing!")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
X_train_sample = joblib.load(X_TRAIN_PATH)

# ✅ Define important features
important_features = [
    "Dst Port", "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts",
    "Flow Byts/s", "Flow Pkts/s", "Pkt Len Max", "Pkt Len Mean",
    "Pkt Len Std", "SYN Flag Cnt", "ACK Flag Cnt", "FIN Flag Cnt"
]

# ✅ SHAP Explainer
shap_explainer = shap.Explainer(model, X_train_sample)

# ✅ Feature explanations
feature_explanations = {
    "Dst Port": "Unusual destination port activity detected, which may indicate unauthorized access attempts.",
    "Flow Duration": "Long flow duration may suggest slow data exfiltration or prolonged attack attempts.",
    "Tot Fwd Pkts": "High number of forward packets can indicate an attempted brute-force attack.",
    "Tot Bwd Pkts": "Large number of backward packets suggests abnormal response behavior.",
    "Flow Byts/s": "Unusually high or low byte flow rate might indicate scanning or data leakage.",
    "Flow Pkts/s": "Irregular packet per second rate may indicate a DoS attack attempt.",
    "Pkt Len Max": "Maximum packet length being too high or low can signal evasion techniques.",
    "Pkt Len Mean": "Mean packet length deviation from the norm may indicate suspicious activity.",
    "Pkt Len Std": "High variation in packet lengths suggests mixed traffic, possibly an attack attempt.",
    "SYN Flag Cnt": "Frequent SYN flag usage may indicate SYN flood attacks or excessive connection attempts.",
    "ACK Flag Cnt": "High ACK flag count suggests response manipulation, potentially avoiding detection.",
    "FIN Flag Cnt": "Multiple FIN flag occurrences indicate possible connection hijacking or stealth scanning."
}

# ✅ Flask App
app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return jsonify({"message": "🚀 Network Intrusion Detection API is running!"})

@app.route("/predict", methods=["POST"])
def predict():
    try:
        # 🔹 Get JSON data
        data = request.get_json()

        # 🔹 Validate input
        if not data or not isinstance(data, dict):
            return jsonify({"error": "Invalid input format. Expected JSON object."}), 400

        # Track prediction time for performance metrics
        start_time = time.time()

        # 🔹 Convert JSON to DataFrame
        df = pd.DataFrame([data])

        # 🔹 Ensure required columns exist
        missing_features = [feat for feat in important_features if feat not in df.columns]
        if missing_features:
            return jsonify({"error": f"Missing features: {missing_features}"}), 400

        df = df[important_features].astype(float)  # Convert to float

        # ✅ Check input shape
        print("📌 Input Shape:", df.shape)

        # 🔹 Scale features
        df_scaled = scaler.transform(df)

        # ✅ Check scaled shape
        print("📌 Scaled Input Shape:", df_scaled.shape)

        # 🔹 Predict
        prediction = model.predict(df_scaled)[0]
        result = "Malicious" if prediction == 1 else "Normal"

        # Calculate prediction probability if model supports it
        try:
            pred_prob = model.predict_proba(df_scaled)[0]
            confidence = pred_prob[1] if prediction == 1 else pred_prob[0]
            confidence = float(round(confidence * 100, 2))  # Convert numpy.float32 to Python float
        except:
            confidence = None

        if result == "Malicious":
            # ✅ SHAP Explanation
            shap_values = shap_explainer(df_scaled)

            # ✅ Ensure SHAP values have the correct shape
            if isinstance(shap_values, list):
                shap_values = shap_values[0]  # Extract values if wrapped in a list

            if hasattr(shap_values, "values") and shap_values.values is not None:
                feature_importance = np.abs(shap_values.values).mean(axis=0)
            else:
                raise ValueError("❌ SHAP values are empty or not computed correctly.")

            # ✅ Debugging SHAP output
            print("📌 SHAP Values Shape:", feature_importance.shape)

            # ✅ Get Top 2 Influential Features
            top_feature_indices = np.argsort(feature_importance)[-2:][::-1]  # Get top 2
            top_features = [important_features[i] for i in top_feature_indices if i < len(important_features)]

            # ✅ Ensure we have at least 1 feature
            if len(top_features) == 0:
                explanation = "No significant features identified."
            elif len(top_features) == 1:
                explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}."
            else:
                explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}. Additionally, {feature_explanations.get(top_features[1], 'Unknown reason')}."

            # ✅ Log Response
            response = {
                "prediction": result,
                "reason": explanation,
                "confidence": confidence,
                "processing_time_ms": float(round((time.time() - start_time) * 1000, 2))  # Convert to Python float
            }
        else:
            response = {
                "prediction": result,
                "confidence": confidence,
                "processing_time_ms": float(round((time.time() - start_time) * 1000, 2))  # Convert to Python float
            }  # No explanation for normal traffic

        print("📌 API Response:", response)
        return jsonify(response)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/batch-predict", methods=["POST"])
def batch_predict():
    try:
        # Get array of data samples
        data_array = request.get_json()
        
        if not data_array or not isinstance(data_array, list):
            return jsonify({"error": "Invalid input format. Expected JSON array."}), 400
            
        results = []
        
        for data in data_array:
            # Process each sample
            df = pd.DataFrame([data])
            
            # Ensure required columns exist
            missing_features = [feat for feat in important_features if feat not in df.columns]
            if missing_features:
                results.append({"error": f"Missing features: {missing_features}"})
                continue
                
            df = df[important_features].astype(float)
            df_scaled = scaler.transform(df)
            
            # Predict
            prediction = model.predict(df_scaled)[0]
            result = "Malicious" if prediction == 1 else "Normal"
            
            if result == "Malicious":
                # SHAP Explanation
                shap_values = shap_explainer(df_scaled)
                
                if isinstance(shap_values, list):
                    shap_values = shap_values[0]
                    
                if hasattr(shap_values, "values") and shap_values.values is not None:
                    feature_importance = np.abs(shap_values.values).mean(axis=0)
                    
                    # Get Top 2 Influential Features
                    top_feature_indices = np.argsort(feature_importance)[-2:][::-1]
                    top_features = [important_features[i] for i in top_feature_indices if i < len(important_features)]
                    
                    if len(top_features) == 0:
                        explanation = "No significant features identified."
                    elif len(top_features) == 1:
                        explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}."
                    else:
                        explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}. Additionally, {feature_explanations.get(top_features[1], 'Unknown reason')}."
                        
                    results.append({"prediction": result, "reason": explanation})
                else:
                    results.append({"prediction": result, "reason": "Could not generate explanation."})
            else:
                results.append({"prediction": result})
                
        return jsonify({"results": results})
                
    except Exception as e:
        print(f"❌ Batch Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)


# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# import joblib
# import os
# import shap
# import numpy as np
# from sklearn.preprocessing import StandardScaler
# import time

# # ✅ Load model, scaler, and sample training data
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
# SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")
# X_TRAIN_PATH = os.path.join(os.path.dirname(__file__), "X_train_sample.pkl")

# if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH) or not os.path.exists(X_TRAIN_PATH):
#     raise FileNotFoundError("❌ Model, scaler, or X_train_sample file is missing!")

# model = joblib.load(MODEL_PATH)
# scaler = joblib.load(SCALER_PATH)
# X_train_sample = joblib.load(X_TRAIN_PATH)

# # ✅ Define important features
# important_features = [
#     "Dst Port", "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts",
#     "Flow Byts/s", "Flow Pkts/s", "Pkt Len Max", "Pkt Len Mean",
#     "Pkt Len Std", "SYN Flag Cnt", "ACK Flag Cnt", "FIN Flag Cnt"
# ]

# # ✅ SHAP Explainer
# shap_explainer = shap.Explainer(model, X_train_sample)

# # ✅ Feature explanations
# feature_explanations = {
#     "Dst Port": "Unusual destination port activity detected, which may indicate unauthorized access attempts.",
#     "Flow Duration": "Long flow duration may suggest slow data exfiltration or prolonged attack attempts.",
#     "Tot Fwd Pkts": "High number of forward packets can indicate an attempted brute-force attack.",
#     "Tot Bwd Pkts": "Large number of backward packets suggests abnormal response behavior.",
#     "Flow Byts/s": "Unusually high or low byte flow rate might indicate scanning or data leakage.",
#     "Flow Pkts/s": "Irregular packet per second rate may indicate a DoS attack attempt.",
#     "Pkt Len Max": "Maximum packet length being too high or low can signal evasion techniques.",
#     "Pkt Len Mean": "Mean packet length deviation from the norm may indicate suspicious activity.",
#     "Pkt Len Std": "High variation in packet lengths suggests mixed traffic, possibly an attack attempt.",
#     "SYN Flag Cnt": "Frequent SYN flag usage may indicate SYN flood attacks or excessive connection attempts.",
#     "ACK Flag Cnt": "High ACK flag count suggests response manipulation, potentially avoiding detection.",
#     "FIN Flag Cnt": "Multiple FIN flag occurrences indicate possible connection hijacking or stealth scanning."
# }

# # ✅ Flask App
# app = Flask(__name__)
# CORS(app)

# @app.route("/")
# def home():
#     return jsonify({"message": "🚀 Network Intrusion Detection API is running!"})

# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         # 🔹 Get JSON data
#         data = request.get_json()

#         # 🔹 Validate input
#         if not data or not isinstance(data, dict):
#             return jsonify({"error": "Invalid input format. Expected JSON object."}), 400

#         # Track prediction time for performance metrics
#         start_time = time.time()

#         # 🔹 Convert JSON to DataFrame
#         df = pd.DataFrame([data])

#         # 🔹 Ensure required columns exist
#         missing_features = [feat for feat in important_features if feat not in df.columns]
#         if missing_features:
#             return jsonify({"error": f"Missing features: {missing_features}"}), 400

#         df = df[important_features].astype(float)  # Convert to float

#         # ✅ Check input shape
#         print("📌 Input Shape:", df.shape)

#         # 🔹 Scale features
#         df_scaled = scaler.transform(df)

#         # ✅ Check scaled shape
#         print("📌 Scaled Input Shape:", df_scaled.shape)

#         # 🔹 Predict
#         prediction = model.predict(df_scaled)[0]
#         result = "Malicious" if prediction == 1 else "Normal"

#         # Calculate prediction probability if model supports it
#         try:
#             pred_prob = model.predict_proba(df_scaled)[0]
#             confidence = pred_prob[1] if prediction == 1 else pred_prob[0]
#             confidence = round(confidence * 100, 2)
#         except:
#             confidence = None

#         if result == "Malicious":
#             # ✅ SHAP Explanation
#             shap_values = shap_explainer(df_scaled)

#             # ✅ Ensure SHAP values have the correct shape
#             if isinstance(shap_values, list):
#                 shap_values = shap_values[0]  # Extract values if wrapped in a list

#             if hasattr(shap_values, "values") and shap_values.values is not None:
#                 feature_importance = np.abs(shap_values.values).mean(axis=0)
#             else:
#                 raise ValueError("❌ SHAP values are empty or not computed correctly.")

#             # ✅ Debugging SHAP output
#             print("📌 SHAP Values Shape:", feature_importance.shape)

#             # ✅ Get Top 2 Influential Features
#             top_feature_indices = np.argsort(feature_importance)[-2:][::-1]  # Get top 2
#             top_features = [important_features[i] for i in top_feature_indices if i < len(important_features)]

#             # ✅ Ensure we have at least 1 feature
#             if len(top_features) == 0:
#                 explanation = "No significant features identified."
#             elif len(top_features) == 1:
#                 explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}."
#             else:
#                 explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}. Additionally, {feature_explanations.get(top_features[1], 'Unknown reason')}."

#             # ✅ Log Response
#             response = {
#                 "prediction": result,
#                 "reason": explanation,
#                 "confidence": float(confidence) if confidence is not None else None,
#                 "processing_time_ms": round((time.time() - start_time) * 1000, 2)
#             }
#         else:
#             response = {
#                 "prediction": result,
#                 "confidence": float(confidence) if confidence is not None else None,
#                 "processing_time_ms": round((time.time() - start_time) * 1000, 2)
#             }  # No explanation for normal traffic

#         print("📌 API Response:", response)
#         return jsonify(response)

#     except Exception as e:
#         print(f"❌ Error: {str(e)}")
#         return jsonify({"error": "Internal server error"}), 500

# @app.route("/batch-predict", methods=["POST"])
# def batch_predict():
#     try:
#         # Get array of data samples
#         data_array = request.get_json()
        
#         if not data_array or not isinstance(data_array, list):
#             return jsonify({"error": "Invalid input format. Expected JSON array."}), 400
            
#         results = []
        
#         for data in data_array:
#             # Process each sample
#             df = pd.DataFrame([data])
            
#             # Ensure required columns exist
#             missing_features = [feat for feat in important_features if feat not in df.columns]
#             if missing_features:
#                 results.append({"error": f"Missing features: {missing_features}"})
#                 continue
                
#             df = df[important_features].astype(float)
#             df_scaled = scaler.transform(df)
            
#             # Predict
#             prediction = model.predict(df_scaled)[0]
#             result = "Malicious" if prediction == 1 else "Normal"
            
#             if result == "Malicious":
#                 # SHAP Explanation
#                 shap_values = shap_explainer(df_scaled)
                
#                 if isinstance(shap_values, list):
#                     shap_values = shap_values[0]
                    
#                 if hasattr(shap_values, "values") and shap_values.values is not None:
#                     feature_importance = np.abs(shap_values.values).mean(axis=0)
                    
#                     # Get Top 2 Influential Features
#                     top_feature_indices = np.argsort(feature_importance)[-2:][::-1]
#                     top_features = [important_features[i] for i in top_feature_indices if i < len(important_features)]
                    
#                     if len(top_features) == 0:
#                         explanation = "No significant features identified."
#                     elif len(top_features) == 1:
#                         explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}."
#                     else:
#                         explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}. Additionally, {feature_explanations.get(top_features[1], 'Unknown reason')}."
                        
#                     results.append({"prediction": result, "reason": explanation})
#                 else:
#                     results.append({"prediction": result, "reason": "Could not generate explanation."})
#             else:
#                 results.append({"prediction": result})
                
#         return jsonify({"results": results})
                
#     except Exception as e:
#         print(f"❌ Batch Error: {str(e)}")
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)



# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import pandas as pd
# import joblib
# import os
# import shap
# import numpy as np
# from sklearn.preprocessing import StandardScaler

# # ✅ Load model, scaler, and sample training data
# MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")
# SCALER_PATH = os.path.join(os.path.dirname(__file__), "scaler.pkl")
# X_TRAIN_PATH = os.path.join(os.path.dirname(__file__), "X_train_sample.pkl")

# if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH) or not os.path.exists(X_TRAIN_PATH):
#     raise FileNotFoundError("❌ Model, scaler, or X_train_sample file is missing!")

# model = joblib.load(MODEL_PATH)
# scaler = joblib.load(SCALER_PATH)
# X_train_sample = joblib.load(X_TRAIN_PATH)

# # ✅ Define important features
# important_features = [
#     "Dst Port", "Flow Duration", "Tot Fwd Pkts", "Tot Bwd Pkts",
#     "Flow Byts/s", "Flow Pkts/s", "Pkt Len Max", "Pkt Len Mean",
#     "Pkt Len Std", "SYN Flag Cnt", "ACK Flag Cnt", "FIN Flag Cnt"
# ]

# # ✅ SHAP Explainer
# shap_explainer = shap.Explainer(model, X_train_sample)

# # ✅ Feature explanations
# feature_explanations = {
#     "Dst Port": "Unusual destination port activity detected, which may indicate unauthorized access attempts.",
#     "Flow Duration": "Long flow duration may suggest slow data exfiltration or prolonged attack attempts.",
#     "Tot Fwd Pkts": "High number of forward packets can indicate an attempted brute-force attack.",
#     "Tot Bwd Pkts": "Large number of backward packets suggests abnormal response behavior.",
#     "Flow Byts/s": "Unusually high or low byte flow rate might indicate scanning or data leakage.",
#     "Flow Pkts/s": "Irregular packet per second rate may indicate a DoS attack attempt.",
#     "Pkt Len Max": "Maximum packet length being too high or low can signal evasion techniques.",
#     "Pkt Len Mean": "Mean packet length deviation from the norm may indicate suspicious activity.",
#     "Pkt Len Std": "High variation in packet lengths suggests mixed traffic, possibly an attack attempt.",
#     "SYN Flag Cnt": "Frequent SYN flag usage may indicate SYN flood attacks or excessive connection attempts.",
#     "ACK Flag Cnt": "High ACK flag count suggests response manipulation, potentially avoiding detection.",
#     "FIN Flag Cnt": "Multiple FIN flag occurrences indicate possible connection hijacking or stealth scanning."
# }

# # ✅ Flask App
# app = Flask(__name__)
# CORS(app)

# @app.route("/")
# def home():
#     return jsonify({"message": "🚀 Network Intrusion Detection API is running!"})

# @app.route("/predict", methods=["POST"])
# def predict():
#     try:
#         # 🔹 Get JSON data
#         data = request.get_json()

#         # 🔹 Validate input
#         if not data or not isinstance(data, dict):
#             return jsonify({"error": "Invalid input format. Expected JSON object."}), 400

#         # 🔹 Convert JSON to DataFrame
#         df = pd.DataFrame([data])

#         # 🔹 Ensure required columns exist
#         missing_features = [feat for feat in important_features if feat not in df.columns]
#         if missing_features:
#             return jsonify({"error": f"Missing features: {missing_features}"}), 400

#         df = df[important_features].astype(float)  # Convert to float

#         # ✅ Check input shape
#         print("📌 Input Shape:", df.shape)

#         # 🔹 Scale features
#         df_scaled = scaler.transform(df)

#         # ✅ Check scaled shape
#         print("📌 Scaled Input Shape:", df_scaled.shape)

#         # 🔹 Predict
#         prediction = model.predict(df_scaled)[0]
#         result = "Malicious" if prediction == 1 else "Normal"

#         if result == "Malicious":
#             # ✅ SHAP Explanation
#             shap_values = shap_explainer(df_scaled)

#             # ✅ Ensure SHAP values have the correct shape
#             if isinstance(shap_values, list):
#                 shap_values = shap_values[0]  # Extract values if wrapped in a list

#             if hasattr(shap_values, "values") and shap_values.values is not None:
#                 feature_importance = np.abs(shap_values.values).mean(axis=0)
#             else:
#                 raise ValueError("❌ SHAP values are empty or not computed correctly.")

#             # ✅ Debugging SHAP output
#             print("📌 SHAP Values Shape:", feature_importance.shape)

#             # ✅ Get Top 2 Influential Features
#             top_feature_indices = np.argsort(feature_importance)[-2:][::-1]  # Get top 2
#             top_features = [important_features[i] for i in top_feature_indices if i < len(important_features)]

#             # ✅ Ensure we have at least 1 feature
#             if len(top_features) == 0:
#                 explanation = "No significant features identified."
#             elif len(top_features) == 1:
#                 explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}."
#             else:
#                 explanation = f"{feature_explanations.get(top_features[0], 'Unknown reason')}. Additionally, {feature_explanations.get(top_features[1], 'Unknown reason')}."

#             # ✅ Log Response
#             response = {"prediction": result, "reason": explanation}
#         else:
#             response = {"prediction": result}  # No explanation for normal traffic

#         print("📌 API Response:", response)
#         return jsonify(response)

#     except Exception as e:
#         print(f"❌ Error: {str(e)}")
#         return jsonify({"error": "Internal server error"}), 500

#     except Exception as e:
#         print("❌ API Error:", str(e))
#         return jsonify({"error": str(e)}), 500

# if __name__ == "__main__":
#     app.run(debug=True)
