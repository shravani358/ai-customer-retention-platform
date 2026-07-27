from datetime import datetime
from services.email_service import send_email
from services.ai import chatbot_reply


def generate_monthly_report(customers: list[dict]) -> bool:
    """Build a monthly analytics report and email it."""

    # ── Crunch the numbers ────────────────────────────────────
    total = len(customers)
    if total == 0:
        return False

    high_risk   = [c for c in customers if c["churn_risk"] >= 0.7]
    medium_risk = [c for c in customers if 0.4 <= c["churn_risk"] < 0.7]
    low_risk    = [c for c in customers if c["churn_risk"] < 0.4]

    avg_risk          = sum(c["churn_risk"] for c in customers) / total
    total_revenue     = sum(c["monthly_charges"] for c in customers)
    revenue_at_risk   = sum(c["monthly_charges"] for c in high_risk)
    avg_tenure        = sum(c["tenure_months"] for c in customers) / total
    avg_tickets       = sum(c["support_tickets"] for c in customers) / total

    month_label = datetime.now().strftime("%B %Y")

    # ── Ask AI for a narrative summary ────────────────────────
    stats_summary = (
        f"Monthly retention report for {month_label}:\n"
        f"- Total customers: {total}\n"
        f"- High risk (>70%): {len(high_risk)} ({len(high_risk)/total*100:.1f}%)\n"
        f"- Medium risk (40-70%): {len(medium_risk)}\n"
        f"- Low risk (<40%): {len(low_risk)}\n"
        f"- Average churn risk: {avg_risk*100:.1f}%\n"
        f"- Total monthly revenue: ${total_revenue:,.2f}\n"
        f"- Monthly revenue at risk: ${revenue_at_risk:,.2f} ({revenue_at_risk/total_revenue*100:.1f}% of total)\n"
        f"- Average customer tenure: {avg_tenure:.1f} months\n"
        f"- Average support tickets per customer: {avg_tickets:.1f}\n"
    )

    ai_narrative = chatbot_reply(
        message=(
            f"Write a concise 3-paragraph executive summary for this monthly "
            f"customer retention report. Focus on: (1) overall health, "
            f"(2) key risks and their business impact, "
            f"(3) top 2-3 recommended actions for next month. "
            f"Be specific with the numbers provided.\n\n{stats_summary}"
        ),
        history=[],
        db_summary=stats_summary,
    )

    # ── Build top 5 high-risk table rows ─────────────────────
    top5 = sorted(high_risk, key=lambda c: c["churn_risk"], reverse=True)[:5]
    risk_rows = ""
    for c in top5:
        color = "#dc3545" if c["churn_risk"] >= 0.85 else "#fd7e14"
        risk_rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #dee2e6">{c['name']}</td>
            <td style="padding:8px;border:1px solid #dee2e6;color:{color};font-weight:bold">
                {c['churn_risk']*100:.1f}%
            </td>
            <td style="padding:8px;border:1px solid #dee2e6">${c['monthly_charges']:,.2f}</td>
            <td style="padding:8px;border:1px solid #dee2e6">{c['tenure_months']} months</td>
        </tr>"""

    if not risk_rows:
        risk_rows = """
        <tr>
            <td colspan="4" style="padding:8px;text-align:center;color:#6c757d">
                No high-risk customers this month 🎉
            </td>
        </tr>"""

    # ── Build the HTML email ──────────────────────────────────
    body = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:750px;margin:auto;color:#333">

      <!-- Header -->
      <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);
                  color:white;padding:30px;border-radius:8px 8px 0 0">
        <h1 style="margin:0;font-size:24px">📊 Monthly Retention Report</h1>
        <p style="margin:8px 0 0;opacity:0.8">{month_label}</p>
      </div>

      <!-- KPI cards -->
      <div style="display:flex;gap:12px;padding:20px;background:#f8f9fa;
                  border:1px solid #dee2e6;border-top:none">
        <div style="flex:1;background:white;padding:16px;border-radius:8px;
                    text-align:center;border:1px solid #dee2e6">
          <div style="font-size:28px;font-weight:bold;color:#1a1a2e">{total}</div>
          <div style="font-size:13px;color:#6c757d">Total Customers</div>
        </div>
        <div style="flex:1;background:white;padding:16px;border-radius:8px;
                    text-align:center;border:1px solid #dee2e6">
          <div style="font-size:28px;font-weight:bold;color:#dc3545">{len(high_risk)}</div>
          <div style="font-size:13px;color:#6c757d">High Risk</div>
        </div>
        <div style="flex:1;background:white;padding:16px;border-radius:8px;
                    text-align:center;border:1px solid #dee2e6">
          <div style="font-size:28px;font-weight:bold;color:#dc3545">
            ${revenue_at_risk:,.0f}
          </div>
          <div style="font-size:13px;color:#6c757d">Revenue at Risk/mo</div>
        </div>
        <div style="flex:1;background:white;padding:16px;border-radius:8px;
                    text-align:center;border:1px solid #dee2e6">
          <div style="font-size:28px;font-weight:bold;color:#0d6efd">
            {avg_risk*100:.0f}%
          </div>
          <div style="font-size:13px;color:#6c757d">Avg Churn Risk</div>
        </div>
      </div>

      <!-- AI narrative -->
      <div style="padding:24px;border:1px solid #dee2e6;border-top:none;background:white">
        <h2 style="margin:0 0 16px;color:#1a1a2e">🤖 AI Executive Summary</h2>
        <div style="background:#f0f4ff;padding:16px;border-radius:8px;
                    border-left:4px solid #0d6efd;line-height:1.7">
          {ai_narrative.replace(chr(10), "<br>")}
        </div>
      </div>

      <!-- Top risk table -->
      <div style="padding:24px;border:1px solid #dee2e6;border-top:none;background:white">
        <h2 style="margin:0 0 16px;color:#1a1a2e">⚠️ Top High-Risk Customers</h2>
        <table style="width:100%;border-collapse:collapse">
          <thead>
            <tr style="background:#f8f9fa">
              <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Customer</th>
              <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Churn Risk</th>
              <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Monthly Value</th>
              <th style="padding:8px;border:1px solid #dee2e6;text-align:left">Tenure</th>
            </tr>
          </thead>
          <tbody>{risk_rows}</tbody>
        </table>
      </div>

      <!-- Risk breakdown -->
      <div style="padding:24px;border:1px solid #dee2e6;border-top:none;background:white">
        <h2 style="margin:0 0 16px;color:#1a1a2e">📈 Risk Breakdown</h2>
        <div style="display:flex;gap:8px">
          <div style="flex:{len(high_risk)};background:#dc3545;height:24px;
                      border-radius:4px 0 0 4px"></div>
          <div style="flex:{len(medium_risk)};background:#ffc107;height:24px"></div>
          <div style="flex:{max(len(low_risk),1)};background:#198754;height:24px;
                      border-radius:0 4px 4px 0"></div>
        </div>
        <div style="display:flex;gap:16px;margin-top:8px;font-size:13px">
          <span>🔴 High: {len(high_risk)}</span>
          <span>🟡 Medium: {len(medium_risk)}</span>
          <span>🟢 Low: {len(low_risk)}</span>
        </div>
      </div>

      <!-- Footer -->
      <div style="padding:16px;text-align:center;background:#f8f9fa;
                  border:1px solid #dee2e6;border-top:none;
                  border-radius:0 0 8px 8px;font-size:13px;color:#6c757d">
        Generated automatically by AI Customer Retention Platform •
        {datetime.now().strftime("%d %b %Y, %H:%M")}
      </div>

    </body></html>
    """

    return send_email(
        subject=f"📊 Monthly Retention Report — {month_label}",
        body_html=body,
    )