# 🔒 AI Customer Retention Platform

> An AI-powered full-stack platform that predicts customer churn, explains risk in plain English, and generates personalized retention strategies — built with Python, FastAPI, Machine Learning, and Generative AI.

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?logo=streamlit)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Live Demo

| Service | URL |
|---|---|
| 🖥️ Dashboard | [retention-platform.streamlit.app](https://retention-platform-vknkgwwjyxyrss52hjpgj6.streamlit.app) |
| ⚡ API Docs | [retention-platform-api.onrender.com/docs](https://retention-platform-api.onrender.com/docs) |

> **Note:** Free tier services sleep after 15 minutes of inactivity. First load may take 30–60 seconds to wake up.

---

## ✨ Features

| Feature | Description |
|---|---|
| 👥 **Customer Management** | Full CRUD with role-based access (Admin / Manager / Analyst) |
| 🤖 **Churn Prediction** | ML model (Random Forest) scores each customer 0–100% risk |
| 💡 **AI Explanations** | Gemini LLM explains *why* a customer is at risk in plain English |
| 🎯 **Retention Strategies** | Personalized, prioritized action plans generated per customer |
| 📊 **Executive Dashboard** | Live KPI cards, risk distribution charts, revenue-at-risk |
| 💬 **Manager Chatbot** | Conversational AI with memory, grounded in live customer data |
| 🔐 **Role-Based Login** | JWT authentication — Admin, Manager, Analyst permission tiers |
| 📧 **Email Alerts** | Automated HTML emails for high-risk customers via Gmail SMTP |
| 📋 **Monthly Reports** | AI-written executive summaries emailed on demand |
| 🐳 **Docker Deployment** | Multi-container Docker Compose setup |
| ☁️ **Cloud Hosted** | FastAPI on Render + Dashboard on Streamlit Community Cloud |
| 🔄 **CI/CD Pipeline** | GitHub Actions auto-deploys on every push to main |

---

## 🛠️ Tech Stack

### Backend
- **FastAPI** — REST API with auto-generated Swagger docs
- **SQLAlchemy** — ORM for database operations
- **SQLite** — Database (swappable with PostgreSQL)
- **Pydantic** — Request/response validation
- **python-jose** — JWT token creation and verification
- **passlib + bcrypt** — Secure password hashing

### Machine Learning & AI
- **scikit-learn** — Random Forest churn prediction model
- **pandas + numpy** — Data processing
- **joblib** — Model serialization (`model.pkl`)
- **Google Gemini API** — LLM for explanations, strategies, chatbot

### Frontend & Dashboard
- **Streamlit** — Multi-page interactive dashboard
- **Plotly** — Interactive charts (histogram, pie, bar)

### Infrastructure
- **Docker + Docker Compose** — Containerization
- **GitHub Actions** — CI/CD pipeline
- **Render** — Cloud API hosting (free tier)
- **Streamlit Community Cloud** — Dashboard hosting (free tier)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│            Browser (User)                        │
└────────────────────┬────────────────────────────┘
                     │ HTTP
                     ▼
┌─────────────────────────────────────────────────┐
│       Streamlit Dashboard (Port 8501)            │
│  Login | Dashboard | Customers | AI | Chatbot   │
└────────────────────┬────────────────────────────┘
                     │ REST API calls + JWT
                     ▼
┌─────────────────────────────────────────────────┐
│         FastAPI Backend (Port 8000)              │
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│  │ Auth     │  │ Customers│  │ Predictions  │  │
│  │ /register│  │ CRUD     │  │ /predict     │  │
│  │ /login   │  │ endpoints│  │ /insights    │  │
│  └──────────┘  └──────────┘  └──────────────┘  │
│                                                  │
│  ┌────────────────────────────────────────────┐ │
│  │              Services Layer                │ │
│  │  ML (model.pkl) | Gemini AI | Email SMTP  │ │
│  └────────────────────────────────────────────┘ │
│                      │                           │
│              SQLite Database                     │
└─────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
ai-customer-retention-platform/
├── backend/
│   └── app/
│       ├── main.py              # FastAPI app + all endpoints
│       ├── database.py          # SQLAlchemy engine + session
│       ├── models.py            # Customer + User DB models
│       ├── schemas.py           # Pydantic request/response schemas
│       ├── security.py          # Password hashing + JWT creation
│       ├── deps.py              # Auth dependencies + role checking
│       ├── config.py            # Environment variable loader
│       ├── dashboard.py         # Streamlit dashboard (all pages)
│       ├── requirements.txt     # Python dependencies
│       ├── Dockerfile           # Container definition
│       ├── .dockerignore
│       ├── .env                 # ← not committed (secrets)
│       ├── ml/
│       │   ├── train_model.py   # Model training script
│       │   ├── predict.py       # Prediction helper
│       │   └── model.pkl        # Trained model (generated)
│       └── services/
│           ├── ai.py            # Gemini LLM calls
│           ├── email_service.py # SMTP email sending
│           └── report_service.py# Monthly report generator
├── docker-compose.yml           # Multi-container orchestration
├── .github/
│   └── workflows/
│       └── deploy.yml           # GitHub Actions CI/CD
└── .gitignore
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Git
- Docker Desktop (optional, for containerized run)

### 1. Clone the repository

```bash
git clone https://github.com/shravani358/ai-customer-retention-platform.git
cd ai-customer-retention-platform
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r backend/app/requirements.txt
```

### 4. Set up environment variables

Create `backend/app/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SECRET_KEY=your_random_secret_key_here
EMAIL_SENDER=yourgmail@gmail.com
EMAIL_PASSWORD="your 16 char app password"
EMAIL_RECEIVER=alerts@yourcompany.com
```

- **Gemini API key** — free at [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
- **SECRET_KEY** — generate with `python -c "import secrets; print(secrets.token_hex(32))"`
- **EMAIL_PASSWORD** — Gmail App Password (not your regular password) from [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

### 5. Train the ML model

```bash
cd backend/app
python ml/train_model.py
```

Expected output:
```
Model trained. Test accuracy: 82.50%
Model saved to .../ml/model.pkl
```

### 6. Run the API

```bash
cd backend/app
uvicorn main:app --reload
```

API available at: **http://127.0.0.1:8000**
Swagger docs at: **http://127.0.0.1:8000/docs**

### 7. Run the dashboard (new terminal)

```bash
cd backend/app
streamlit run dashboard.py
```

Dashboard available at: **http://localhost:8501**

---

## 🐳 Docker Setup

```bash
# From project root
docker-compose up --build
```

- API: http://localhost:8000/docs
- Dashboard: http://localhost:8501

---

## 🔐 Default Test Users

Register these via **POST /auth/register** in Swagger docs:

| Email | Password | Role | Access |
|---|---|---|---|
| admin@test.com | admin123 | admin | Full access |
| manager@test.com | manager123 | manager | AI insights + chatbot |
| analyst@test.com | analyst123 | analyst | View + predictions only |

---

## 📡 API Endpoints

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Register new user |
| POST | `/auth/login` | Public | Login, returns JWT token |
| GET | `/customers` | Any | List all customers |
| POST | `/customers` | Admin | Create customer |
| PUT | `/customers/{id}` | Admin | Update customer |
| DELETE | `/customers/{id}` | Admin | Delete customer |
| POST | `/customers/{id}/predict` | Any | Run churn prediction |
| GET | `/customers/{id}/insights` | Admin, Manager | AI explanation + strategy |
| POST | `/chatbot` | Admin, Manager | AI chatbot with memory |
| POST | `/alerts/high-risk` | Admin, Manager | Send email alert |
| POST | `/reports/monthly` | Admin, Manager | Send monthly report |

---

## 🤖 How the AI Works

### Churn Prediction
A **Random Forest Classifier** trained on 4 customer behavior features:
- `tenure_months` — how long they have been a customer
- `monthly_charges` — what they pay per month
- `support_tickets` — number of support issues filed
- `last_login_days` — days since last platform login

Returns a **probability score (0.0–1.0)** — e.g., `0.985` = 98.5% likely to churn.

### AI Explanation
The churn score + customer data is sent to **Google Gemini** with a targeted prompt:
```
"You are a customer retention analyst. Explain churn risk clearly
for a business manager in 3-4 sentences. Base your explanation
only on the data given."
```
Result: grounded, plain-English explanation referencing actual numbers.

### Chatbot Memory
Conversation history is passed on every API call as a list of `{role, content}` dicts.
The AI sees the full conversation thread, enabling natural multi-turn dialogue grounded
in live customer data.

---

## ☁️ Deployment

### Render (API)
1. Connect GitHub repo to [render.com](https://render.com)
2. Set Root Directory: `backend/app`, Runtime: `Docker`
3. Add environment variables in Render dashboard
4. Auto-deploys on every push via GitHub Actions

### Streamlit Community Cloud (Dashboard)
1. Connect GitHub repo at [share.streamlit.io](https://share.streamlit.io)
2. Set main file: `backend/app/dashboard.py`
3. Add secret: `API_URL = "https://your-app.onrender.com"`

---

## 🔄 CI/CD Pipeline

Every `git push` to `main` triggers:
1. GitHub Actions checks out code
2. Installs Python 3.12 + dependencies
3. Runs tests
4. Calls Render deploy hook → automatic redeployment

```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]
```

---

## 📊 Sample Output

**Churn Risk Score:** `0.985` (98.5%)

**AI Explanation:**
> *"Risky Corp is at an extremely high churn risk because they have not logged into
> the platform for 80 days, suggesting they have already abandoned the service.
> Furthermore, despite only having a two-month tenure, the account has generated
> six support tickets, indicating significant unresolved frustration or technical
> barriers."*

**Retention Strategy:**
> *"1. Execute a High-Touch Recovery Outreach (Priority: Immediate) — have an Account
> Manager send a personalized video message acknowledging the specific pain points
> identified in their tickets..."*

---

## 🗺️ Roadmap

- [ ] Alembic database migrations for safe schema evolution
- [ ] pytest test suite with coverage reporting
- [ ] PostgreSQL for production deployments
- [ ] SHAP value visualizations per customer
- [ ] Celery + Redis for scheduled background jobs
- [ ] Customer churn history timeline charts
- [ ] React frontend for production UI

---

## 📄 License

This project is licensed under the MIT License.

---

## 👩‍💻 Author

**Shravani Margal**

Built from scratch

[![GitHub](https://img.shields.io/badge/GitHub-shravani358-black?logo=github)](https://github.com/shravani358)

---

*Built with 🤖 AI assistance and a lot of debugging*
