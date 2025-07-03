# Network Intrusion Detection System


Network Intrusion Detection System (NIDS)

 Overview

This project is a Network Intrusion Detection System (NIDS) that classifies network traffic as Normal or Malicious using Machine Learning. It provides detailed explanations for malicious detections.

📂 Project Structure

graphql
Copy code

NIDS/
│── backend/          # Flask API and ML Model
│── frontend/         # React-based UI
│── dataset/          # Network Traffic Data (Ignored in Git)
│── README.md         # Project Documentation
│── .gitignore        # Ignoring large files like datasets and node_modules

🛠️ Installation & Setup

📌 Backend (Flask API)

Navigate to the backend folder:

powershell
Copy code

1. cd backend

Create a virtual environment & activate it:
powershell
Copy code

2.   _python -m venv venv
  venv\Scripts\activate_ # Windows

Install dependencies:

powershell
Copy code

3. pip install -r requirements.txt

Run the Flask server:

powershell
Copy code

4. python app.py

📌 Frontend (React)

Navigate to the frontend folder:

powershell
Copy code

1. cd frontend

Install dependencies:

powershell
Copy code

2. npm install

Run the frontend server:

powershell
Copy code

3. npm start

🚀 How to Use

1. Enter network parameters in the UI.

2. Click Predict.

The system will classify the traffic as Normal or Malicious.
If malicious, a detailed explanation is provided.

🔗 API Endpoints

POST /predict → Predicts network traffic behavior.

📌 Important Notes

Dataset files are not included in this repo.
To retrain the model, use train_model.py.
Ensure Flask runs on http://127.0.0.1:5000/ before starting the frontend.
