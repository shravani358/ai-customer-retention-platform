import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER


def send_email(subject: str, body_html: str):
    """Send an HTML email via Gmail SMTP."""
    if not EMAIL_SENDER or not EMAIL_PASSWORD or not EMAIL_RECEIVER:
        print("Email not configured — skipping send.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg.attach(MIMEText(body_html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())

        print(f"Email sent: {subject}")
        return True

    except Exception as e:
        print(f"Email failed: {e}")
        return False


def send_high_risk_alert(customers: list[dict]):
    """Build and send a high-risk customer alert email."""
    if not customers:
        return False

    rows = ""
    for c in customers:
        risk_pct = f"{c['churn_risk'] * 100:.1f}%"
        color = "#dc3545" if c["churn_risk"] >= 0.85 else "#fd7e14"
        rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #dee2e6">{c['name']}</td>
            <td style="padding:8px;border:1px solid #dee2e6">{c['email']}</td>
            <td style="padding:8px;border:1px solid #dee2e6;color:{color};font-weight:bold">{risk_pct}</td>
            <td style="padding:8px;border:1px solid #dee2e6">{c['tenure_months']} months</td>
            <td style="padding:8px;border:1px solid #dee2e6">{c['support_tickets']} tickets</td>
        </tr>
        """

    body = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:700px;margin:auto">
        <div style="background:#dc3545;color:white;padding:20px;border-radius:8px 8px 0 0">
            <h2 style="margin:0">⚠️ High Churn Risk Alert</h2>
            <p style="margin:5px 0 0">
                {len(customers)} customer(s) require immediate attention
            </p>
        </div>
        <div style="padding:20px;border:1px solid #dee2e6;border-top:none;border-radius:0 0 8px 8px">
            <table style="width:100%;border-collapse:collapse">
                <thead>
                    <tr style="background:#f8f9fa">
                        <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Customer</th>
                        <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Email</th>
                        <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Churn Risk</th>
                        <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Tenure</th>
                        <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Support Tickets</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
            <p style="margin-top:20px;color:#6c757d;font-size:14px">
                Please log in to the retention platform to view AI insights
                and retention strategies for these customers.
            </p>
        </div>
    </body></html>
    """

    return send_email(
        subject=f"🚨 {len(customers)} High-Risk Customer(s) Need Attention",
        body_html=body,
    )