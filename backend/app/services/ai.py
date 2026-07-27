from google import genai
from google.genai import types
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-flash-lite-latest"

def explain_churn(customer: dict) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=(
            f"Customer: {customer['name']}\n"
            f"Tenure: {customer['tenure_months']} months\n"
            f"Monthly charges: ${customer['monthly_charges']}\n"
            f"Support tickets: {customer['support_tickets']}\n"
            f"Days since last login: {customer['last_login_days']}\n"
            f"Predicted churn probability: {customer['churn_risk']}\n\n"
            "Explain why this customer may be at risk of leaving."
        ),
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a customer retention analyst. Explain churn risk "
                "clearly and concretely for a business manager, in 3-4 sentences. "
                "Base your explanation only on the data given."
            ),
        ),
    )
    return response.text


def suggest_retention_strategy(customer: dict) -> str:
    response = client.models.generate_content(
        model=MODEL,
        contents=(
            f"Customer: {customer['name']}\n"
            f"Tenure: {customer['tenure_months']} months\n"
            f"Monthly charges: ${customer['monthly_charges']}\n"
            f"Support tickets: {customer['support_tickets']}\n"
            f"Days since last login: {customer['last_login_days']}\n"
            f"Predicted churn probability: {customer['churn_risk']}\n\n"
            "Suggest 3 prioritized retention actions for this customer."
        ),
        config=types.GenerateContentConfig(
            system_instruction=(
                "You design personalized, actionable retention strategies "
                "for at-risk customers. Give 3 specific, prioritized actions."
            ),
        ),
    )
    return response.text

def chatbot_reply(message: str, history: list[dict], db_summary: str) -> str:
    convo = ""
    for turn in history:
        speaker = "Manager" if turn["role"] == "user" else "Assistant"
        convo += f"{speaker}: {turn['content']}\n"
    convo += f"Manager: {message}\n"

    response = client.models.generate_content(
        model=MODEL,
        contents=convo,
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a helpful retention assistant for business managers. "
                "Answer questions about customers and churn risk using only the "
                "data provided below. Be concise and specific.\n\n"
                f"Current customer data:\n{db_summary}"
            ),
        ),
    )
    return response.text