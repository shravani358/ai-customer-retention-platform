import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib
import os

# These are the customer fields our model will learn from
FEATURES = ["tenure_months", "monthly_charges", "support_tickets", "last_login_days"]

def generate_fake_data(n=1000):
    """Creates realistic-looking fake customers with a churn pattern baked in,
    so the model has something real to learn from."""
    rng = np.random.default_rng(42)

    tenure_months = rng.integers(0, 72, n)
    monthly_charges = rng.uniform(20, 150, n)
    support_tickets = rng.poisson(2, n)
    last_login_days = rng.integers(0, 90, n)

    # Simple made-up rule: short tenure + many tickets + inactivity = higher churn chance
    risk_score = (
        (72 - tenure_months) / 72 * 0.4
        + (support_tickets / 10) * 0.3
        + (last_login_days / 90) * 0.3
    )
    churn_prob = np.clip(risk_score + rng.normal(0, 0.1, n), 0, 1)
    churn = (churn_prob > 0.5).astype(int)

    return pd.DataFrame({
        "tenure_months": tenure_months,
        "monthly_charges": monthly_charges,
        "support_tickets": support_tickets,
        "last_login_days": last_login_days,
        "churn": churn,
    })

def train():
    df = generate_fake_data()
    X, y = df[FEATURES], df["churn"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(n_estimators=200, random_state=42)),
    ])
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"Model trained. Test accuracy: {accuracy:.2%}")

    # Save the trained model right next to this script
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()