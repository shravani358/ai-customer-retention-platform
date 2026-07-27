from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from services.email_service import send_high_risk_alert
from services.report_service import generate_monthly_report

from database import engine, get_db, Base
import models, schemas, security, deps
from ml.predict import predict_churn
from services.ai import explain_churn, suggest_retention_strategy, chatbot_reply

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "It works! My retention platform is alive."}


# ---------- Auth ----------

@app.post("/auth/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = models.User(
        email=user.email,
        hashed_password=security.hash_password(user.password),
        role=user.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = security.create_access_token(user.email, user.role)
    return {"access_token": token, "token_type": "bearer"}


# ---------- Customers ----------

@app.get("/customers", response_model=list[schemas.CustomerOut])
def list_customers(db: Session = Depends(get_db), current_user: dict = Depends(deps.get_current_user)):
    return db.query(models.Customer).all()


@app.post("/customers", response_model=schemas.CustomerOut)
def create_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.require_role("admin")),
):
    new = models.Customer(**customer.model_dump())
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@app.put("/customers/{customer_id}", response_model=schemas.CustomerOut)
def update_customer(
    customer_id: int,
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.require_role("admin")),
):
    existing = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
    existing.name = customer.name
    existing.email = customer.email
    existing.tenure_months = customer.tenure_months
    existing.monthly_charges = customer.monthly_charges
    existing.support_tickets = customer.support_tickets
    existing.last_login_days = customer.last_login_days
    existing.churn_risk = customer.churn_risk
    db.commit()
    db.refresh(existing)
    return existing


@app.delete("/customers/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.require_role("admin")),
):
    existing = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(existing)
    db.commit()
    return {"message": f"Customer {customer_id} deleted"}


# ---------- Prediction & AI ----------

@app.post("/customers/{customer_id}/predict", response_model=schemas.CustomerOut)
def predict_customer_churn(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.get_current_user),
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    features = {
        "tenure_months": customer.tenure_months,
        "monthly_charges": customer.monthly_charges,
        "support_tickets": customer.support_tickets,
        "last_login_days": customer.last_login_days,
    }
    customer.churn_risk = predict_churn(features)
    db.commit()
    db.refresh(customer)
    return customer


@app.get("/customers/{customer_id}/insights")
def get_customer_insights(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.require_role("admin", "manager")),
):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    customer_data = {
        "name": customer.name,
        "tenure_months": customer.tenure_months,
        "monthly_charges": customer.monthly_charges,
        "support_tickets": customer.support_tickets,
        "last_login_days": customer.last_login_days,
        "churn_risk": customer.churn_risk,
    }
    return {
        "explanation": explain_churn(customer_data),
        "strategy": suggest_retention_strategy(customer_data),
    }


def build_customer_summary(db: Session) -> str:
    customers = db.query(models.Customer).all()
    if not customers:
        return "No customers in the database yet."
    lines = [
        f"- {c.name}: churn risk {c.churn_risk}, tenure {c.tenure_months} months, "
        f"{c.support_tickets} support tickets, last login {c.last_login_days} days ago"
        for c in customers
    ]
    return "\n".join(lines)


@app.post("/chatbot", response_model=schemas.ChatResponse)
def chat_with_bot(
    request: schemas.ChatRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.require_role("admin", "manager")),
):
    db_summary = build_customer_summary(db)
    history_dicts = [h.model_dump() for h in request.history]
    reply = chatbot_reply(request.message, history_dicts, db_summary)

    updated_history = request.history + [
        schemas.ChatMessage(role="user", content=request.message),
        schemas.ChatMessage(role="assistant", content=reply),
    ]
    return schemas.ChatResponse(reply=reply, history=updated_history)

@app.post("/alerts/high-risk")
def send_high_risk_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.require_role("admin", "manager")),
):
    high_risk = db.query(models.Customer).filter(
        models.Customer.churn_risk >= 0.7
    ).all()

    if not high_risk:
        return {"message": "No high-risk customers found", "sent": False}

    customers_data = [
        {
            "name": c.name,
            "email": c.email,
            "churn_risk": c.churn_risk,
            "tenure_months": c.tenure_months,
            "support_tickets": c.support_tickets,
        }
        for c in high_risk
    ]

    success = send_high_risk_alert(customers_data)
    return {
        "message": f"Alert sent for {len(high_risk)} high-risk customers" if success else "Email failed — check terminal",
        "sent": success,
        "customers": [c["name"] for c in customers_data],
    }

@app.post("/reports/monthly")
def send_monthly_report(
    db: Session = Depends(get_db),
    current_user: dict = Depends(deps.require_role("admin", "manager")),
):
    customers = db.query(models.Customer).all()
    if not customers:
        return {"message": "No customers to report on", "sent": False}

    customers_data = [
        {
            "name": c.name,
            "email": c.email,
            "churn_risk": c.churn_risk,
            "monthly_charges": c.monthly_charges,
            "tenure_months": c.tenure_months,
            "support_tickets": c.support_tickets,
            "last_login_days": c.last_login_days,
        }
        for c in customers
    ]

    success = generate_monthly_report(customers_data)
    return {
        "message": "Monthly report sent successfully!" if success else "Report failed — check terminal",
        "sent": success,
        "customers_included": len(customers_data),
    }