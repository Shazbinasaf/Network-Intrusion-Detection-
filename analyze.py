import requests
import pandas as pd

# ✅ API Endpoint
URL = "http://127.0.0.1:5000/predict"

# ✅ Sample Test Cases with Expected Predictions
test_cases = [
    # ✅ Normal Traffic (Safe Browsing)
    {
        "input": {"Dst Port": 80, "Flow Duration": 50000, "Tot Fwd Pkts": 50, "Tot Bwd Pkts": 40,
                  "Flow Byts/s": 100000, "Flow Pkts/s": 100, "Pkt Len Max": 1000, "Pkt Len Mean": 500,
                  "Pkt Len Std": 200, "SYN Flag Cnt": 1, "ACK Flag Cnt": 1, "FIN Flag Cnt": 0},
        "expected": "Normal"
    },

    # 🚨 Bruteforce SSH Attack
    {
        "input": {"Dst Port": 22, "Flow Duration": 1000000, "Tot Fwd Pkts": 500, "Tot Bwd Pkts": 400,
                  "Flow Byts/s": 2000000, "Flow Pkts/s": 300, "Pkt Len Max": 1400, "Pkt Len Mean": 600,
                  "Pkt Len Std": 250, "SYN Flag Cnt": 50, "ACK Flag Cnt": 45, "FIN Flag Cnt": 0},
        "expected": "Malicious"
    }
    
]

# ✅ Store results
results = []

print("\n📌 Sending test requests to API...\n")
for i, case in enumerate(test_cases):
    response = requests.post(URL, json=case["input"])
    
    if response.status_code == 200:
        data = response.json()
        prediction = data.get("prediction", "Error")
        reason = data.get("reason", "No explanation available.")
        
        results.append({"Test Case": i+1, "Prediction": prediction, "Expected": case["expected"], "Reason": reason})
        
        # ✅ Print result
        status = "✅ PASS" if prediction == case["expected"] else "❌ FAIL"
        print(f"Test {i+1}: {prediction} ➡ {status}")
        print(f"Reason: {reason}\n")
    else:
        print(f"Test {i+1}: ❌ API Error {response.status_code}")

# ✅ Convert to DataFrame for better readability
df_results = pd.DataFrame(results)

# ✅ Print Summary
print("\n🎯 **Final Test Results**")
print(df_results)

# ✅ Save report
df_results.to_csv("test_results.csv", index=False)
print("\n✅ Results saved as 'test_results.csv'")
