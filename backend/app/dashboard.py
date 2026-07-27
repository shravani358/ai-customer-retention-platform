import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

import os
API = os.getenv("API_URL", "http://127.0.0.1:8000")

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Customer Retention Platform",
    page_icon="📊",
    layout="wide"
)

# ── Session state for auth ───────────────────────────────────
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "email" not in st.session_state:
    st.session_state.email = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


# ── Login screen ─────────────────────────────────────────────
def show_login():
    st.title("🔐 AI Customer Retention Platform")
    st.subheader("Please log in to continue")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):
            resp = requests.post(
                f"{API}/auth/login",
                data={"username": email, "password": password},
            )
            if resp.status_code == 200:
                data = resp.json()
                st.session_state.token = data["access_token"]

                # Decode role from token
                import base64, json
                payload = data["access_token"].split(".")[1]
                payload += "=" * (4 - len(payload) % 4)
                decoded = json.loads(base64.b64decode(payload))
                st.session_state.role = decoded.get("role")
                st.session_state.email = decoded.get("sub")
                st.rerun()
            else:
                st.error("Invalid email or password")


# ── Load customers from API ───────────────────────────────────
def load_customers():
    resp = requests.get(f"{API}/customers", headers=auth_headers())
    if resp.status_code == 200:
        return pd.DataFrame(resp.json())
    return pd.DataFrame()


# ── Main dashboard ────────────────────────────────────────────
def show_dashboard():
    # Sidebar
    with st.sidebar:
        st.title("📊 Retention Platform")
        st.markdown(f"**Logged in as:** {st.session_state.email}")
        st.markdown(f"**Role:** `{st.session_state.role}`")
        st.divider()
        page = st.radio(
            "Navigate",
            ["Executive Dashboard", "Customer Management", "AI Insights", "Chatbot"],
        )
        st.divider()
        if st.button("Logout"):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.email = None
            st.rerun()

    df = load_customers()

    # ── Executive Dashboard ───────────────────────────────────
    if page == "Executive Dashboard":
        st.title("📈 Executive Dashboard")

        # Monthly report button
        st.divider()
        st.subheader("📋 Monthly Report")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.caption(
                "Generates a full analytics report with AI executive summary "
                "and emails it to your management team."
            )
        with col2:
            if st.session_state.role in ["admin", "manager"]:
                if st.button("📧 Send Monthly Report", use_container_width=True):
                    with st.spinner("Generating AI report..."):
                        resp = requests.post(
                            f"{API}/reports/monthly",
                            headers=auth_headers()
                        )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data["sent"]:
                            st.success(f"✅ {data['message']}")
                        else:
                            st.warning(data["message"])
                    else:
                        st.error("Failed to generate report")

        if df.empty:
            st.warning("No customer data yet. Add some customers first.")
            return

        high_risk = df[df["churn_risk"] >= 0.7]
        medium_risk = df[(df["churn_risk"] >= 0.4) & (df["churn_risk"] < 0.7)]
        low_risk = df[df["churn_risk"] < 0.4]

        # KPI cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Customers", len(df))
        col2.metric("🔴 High Risk", len(high_risk))
        col3.metric("🟡 Medium Risk", len(medium_risk))
        col4.metric("🟢 Low Risk", len(low_risk))

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Churn Risk Distribution")
            fig = px.histogram(
                df, x="churn_risk", nbins=10,
                color_discrete_sequence=["#636EFA"],
                labels={"churn_risk": "Churn Risk Score"},
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Risk Breakdown")
            risk_counts = pd.DataFrame({
                "Risk Level": ["High Risk", "Medium Risk", "Low Risk"],
                "Count": [len(high_risk), len(medium_risk), len(low_risk)],
            })
            fig2 = px.pie(
                risk_counts, values="Count", names="Risk Level",
                color_discrete_sequence=["#EF553B", "#FFA15A", "#00CC96"],
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Revenue at Risk")
        if "monthly_charges" in df.columns:
            revenue_at_risk = high_risk["monthly_charges"].sum()
            total_revenue = df["monthly_charges"].sum()
            st.metric(
                "Monthly Revenue at Risk (High Risk Customers)",
                f"${revenue_at_risk:,.2f}",
                delta=f"-{revenue_at_risk/total_revenue*100:.1f}% of total" if total_revenue > 0 else None,
                delta_color="inverse",
            )

            fig3 = px.bar(
                df.sort_values("churn_risk", ascending=False).head(10),
                x="name", y="churn_risk",
                color="churn_risk",
                color_continuous_scale="RdYlGn_r",
                title="Top 10 Highest Risk Customers",
                labels={"churn_risk": "Churn Risk", "name": "Customer"},
            )
            st.plotly_chart(fig3, use_container_width=True)

    # ── Customer Management ───────────────────────────────────
    elif page == "Customer Management":
        st.title("👥 Customer Management")

        if not df.empty:
            st.dataframe(
                df.style.background_gradient(subset=["churn_risk"], cmap="RdYlGn_r"),
                use_container_width=True,
            )
        else:
            st.info("No customers yet.")

        # Alert button — visible to admin and manager
        st.divider()
        col1, col2 = st.columns([2, 1])
        with col1:
            high_risk_count = len(df[df["churn_risk"] >= 0.7]) if not df.empty else 0
            st.metric("High Risk Customers", high_risk_count)
        with col2:
            if st.session_state.role in ["admin", "manager"]:
                if st.button("📧 Send High-Risk Alert Email", use_container_width=True):
                    resp = requests.post(
                        f"{API}/alerts/high-risk",
                        headers=auth_headers()
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        if data["sent"]:
                            st.success(f"✅ {data['message']}")
                        else:
                            st.warning(data["message"])
                    else:
                        st.error("Failed to send alert")

        # Add customer form — admin only
        if st.session_state.role == "admin":
            st.divider()
            st.subheader("➕ Add New Customer")
            with st.form("add_customer"):
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("Company Name")
                    email = st.text_input("Email")
                    tenure = st.number_input("Tenure (months)", 0, 120, 12)
                with col2:
                    charges = st.number_input("Monthly Charges ($)", 0.0, 1000.0, 50.0)
                    tickets = st.number_input("Support Tickets", 0, 50, 0)
                    last_login = st.number_input("Days Since Last Login", 0, 365, 7)

                if st.form_submit_button("Add Customer", use_container_width=True):
                    resp = requests.post(
                        f"{API}/customers",
                        json={
                            "name": name, "email": email,
                            "tenure_months": tenure,
                            "monthly_charges": charges,
                            "support_tickets": tickets,
                            "last_login_days": last_login,
                        },
                        headers=auth_headers(),
                    )
                    if resp.status_code == 200:
                        st.success(f"Customer '{name}' added!")
                        st.rerun()
                    else:
                        st.error("Failed to add customer.")
    # ── AI Insights ───────────────────────────────────────────
    elif page == "AI Insights":
        st.title("🤖 AI Insights")

        if st.session_state.role not in ["admin", "manager"]:
            st.error("You don't have permission to view AI insights.")
            return

        if df.empty:
            st.warning("No customers found.")
            return

        customer_names = df["name"].tolist()
        selected = st.selectbox("Select a customer", customer_names)
        customer_row = df[df["name"] == selected].iloc[0]
        customer_id = int(customer_row["id"])

        col1, col2 = st.columns(2)
        col1.metric("Current Churn Risk", f"{customer_row['churn_risk']:.1%}")
        col2.metric("Tenure", f"{customer_row['tenure_months']} months")

        if st.button("🔮 Run Prediction + Get AI Insights"):
            with st.spinner("Running churn model..."):
                requests.post(
                    f"{API}/customers/{customer_id}/predict",
                    headers=auth_headers()
                )
            with st.spinner("Asking AI for insights..."):
                resp = requests.get(
                    f"{API}/customers/{customer_id}/insights",
                    headers=auth_headers()
                )
            if resp.status_code == 200:
                data = resp.json()
                st.subheader("🔍 Why This Customer May Leave")
                st.info(data["explanation"])
                st.subheader("💡 Recommended Retention Strategy")
                st.success(data["strategy"])
            else:
                st.error("Failed to get insights.")

    # ── Chatbot ───────────────────────────────────────────────
    elif page == "Chatbot":
        st.title("💬 Manager Chatbot")

        if st.session_state.role not in ["admin", "manager"]:
            st.error("Chatbot is only available to managers and admins.")
            return

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        if prompt := st.chat_input("Ask about your customers..."):
            st.session_state.chat_history.append(
                {"role": "user", "content": prompt}
            )
            with st.chat_message("user"):
                st.write(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    resp = requests.post(
                        f"{API}/chatbot",
                        json={
                            "message": prompt,
                            "history": st.session_state.chat_history[:-1],
                        },
                        headers=auth_headers(),
                    )
                if resp.status_code == 200:
                    reply = resp.json()["reply"]
                    st.write(reply)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": reply}
                    )
                else:
                    st.error("Chatbot unavailable right now.")


# ── Entry point ───────────────────────────────────────────────
if st.session_state.token is None:
    show_login()
else:
    show_dashboard()