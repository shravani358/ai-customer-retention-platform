import os
import joblib

FEATURES = ["tenure_months", "monthly_charges", "support_tickets", "last_login_days"]

# Load the trained model once, when the app starts — not on every request
_model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
_model = joblib.load(_model_path)

def predict_churn(customer_data: dict) -> float:
    """Takes a dict with the four feature values and returns a churn probability 0-1."""
    row = [[customer_data[f] for f in FEATURES]]
    probability = _model.predict_proba(row)[0][1]  # [1] = probability of "will churn"
    return round(float(probability), 4)