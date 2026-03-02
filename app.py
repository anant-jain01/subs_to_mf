"""
Subscription Opportunity Cost Calculator (India Edition)
=========================================================
A Streamlit app to visualize the "True Cost" of monthly subscriptions
by comparing them against SIP returns in Indian market instruments.

Author: Built with Streamlit, Plotly, Pandas, and xlsxwriter.
"""

import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# ── Optional scraping ──────────────────────────────────────────────────────────
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
# 1. CONFIGURATION & CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

PRICING_DATABASE: dict[str, dict] = {
    "netflix standard":     {"price": 499,  "display": "Netflix (Standard)",      "category": "Entertainment"},
    "netflix basic":        {"price": 199,  "display": "Netflix (Basic)",          "category": "Entertainment"},
    "netflix mobile":       {"price": 149,  "display": "Netflix (Mobile)",         "category": "Entertainment"},
    "amazon prime":         {"price": 299,  "display": "Amazon Prime",             "category": "Entertainment"},
    "prime video":          {"price": 299,  "display": "Amazon Prime Video",       "category": "Entertainment"},
    "youtube premium":      {"price": 149,  "display": "YouTube Premium",          "category": "Entertainment"},
    "youtube":              {"price": 149,  "display": "YouTube Premium",          "category": "Entertainment"},
    "zomato gold":          {"price": 100,  "display": "Zomato Gold",              "category": "Food & Delivery"},
    "zomato":               {"price": 100,  "display": "Zomato Gold",              "category": "Food & Delivery"},
    "swiggy one":           {"price": 150,  "display": "Swiggy One",               "category": "Food & Delivery"},
    "swiggy":               {"price": 150,  "display": "Swiggy One",               "category": "Food & Delivery"},
    "spotify premium":      {"price": 119,  "display": "Spotify Premium",          "category": "Music"},
    "spotify":              {"price": 119,  "display": "Spotify Premium",          "category": "Music"},
    "disney+ hotstar":      {"price": 299,  "display": "Disney+ Hotstar",          "category": "Entertainment"},
    "hotstar":              {"price": 299,  "display": "Disney+ Hotstar",          "category": "Entertainment"},
    "disney hotstar":       {"price": 299,  "display": "Disney+ Hotstar",          "category": "Entertainment"},
    "apple music":          {"price": 99,   "display": "Apple Music",              "category": "Music"},
    "sony liv":             {"price": 299,  "display": "SonyLIV",                  "category": "Entertainment"},
    "sonyliv":              {"price": 299,  "display": "SonyLIV",                  "category": "Entertainment"},
    "zee5":                 {"price": 149,  "display": "ZEE5",                     "category": "Entertainment"},
    "jio cinema":           {"price": 29,   "display": "JioCinema Premium",        "category": "Entertainment"},
    "jiocinema":            {"price": 29,   "display": "JioCinema Premium",        "category": "Entertainment"},
    "mxplayer":             {"price": 99,   "display": "MX Player Pro",            "category": "Entertainment"},
    "mx player":            {"price": 99,   "display": "MX Player Pro",            "category": "Entertainment"},
    "linkedin premium":     {"price": 1300, "display": "LinkedIn Premium",         "category": "Professional"},
    "linkedin":             {"price": 1300, "display": "LinkedIn Premium",         "category": "Professional"},
    "adobe creative cloud": {"price": 1675, "display": "Adobe Creative Cloud",     "category": "Productivity"},
    "adobe":                {"price": 1675, "display": "Adobe Creative Cloud",     "category": "Productivity"},
    "microsoft 365":        {"price": 420,  "display": "Microsoft 365 Personal",   "category": "Productivity"},
    "microsoft":            {"price": 420,  "display": "Microsoft 365 Personal",   "category": "Productivity"},
    "google one":           {"price": 130,  "display": "Google One (100 GB)",      "category": "Storage"},
    "dropbox":              {"price": 800,  "display": "Dropbox Plus",             "category": "Storage"},
    "icloud":               {"price": 75,   "display": "iCloud+ (50 GB)",          "category": "Storage"},
    "gympass":              {"price": 599,  "display": "Gympass",                  "category": "Health & Fitness"},
    "cult fit":             {"price": 999,  "display": "Cult.fit",                 "category": "Health & Fitness"},
    "cultfit":              {"price": 999,  "display": "Cult.fit",                 "category": "Health & Fitness"},
    "duolingo plus":        {"price": 399,  "display": "Duolingo Plus",            "category": "Education"},
    "duolingo":             {"price": 399,  "display": "Duolingo Plus",            "category": "Education"},
    "coursera plus":        {"price": 3000, "display": "Coursera Plus",            "category": "Education"},
}

BENCHMARKS = {
    "FD (6% p.a.)":          {"rate": 6.0,  "color": "#4FC3F7", "icon": "🏦"},
    "Debt Fund (8% p.a.)":   {"rate": 8.0,  "color": "#81C784", "icon": "📊"},
    "Equity Fund (12% p.a.)":{"rate": 12.0, "color": "#FFB74D", "icon": "🚀"},
}

HORIZON_MONTHS = 120  # 10 years


# ══════════════════════════════════════════════════════════════════════════════
# 2. CORE MATH
# ══════════════════════════════════════════════════════════════════════════════

def sip_future_value(monthly_amount: float, annual_rate_pct: float, months: int) -> float:
    """Annuity-Due Future Value: FV = P × [((1+r)^n - 1) / r] × (1+r)"""
    if annual_rate_pct == 0 or monthly_amount == 0:
        return monthly_amount * months
    r = annual_rate_pct / 12 / 100
    fv = monthly_amount * (((1 + r) ** months - 1) / r) * (1 + r)
    return round(fv, 2)


def build_growth_series(monthly_amount: float, annual_rate_pct: float, months: int) -> np.ndarray:
    """Month-by-month cumulative SIP value for chart."""
    r = annual_rate_pct / 12 / 100
    series = np.zeros(months)
    for n in range(1, months + 1):
        if annual_rate_pct == 0:
            series[n - 1] = monthly_amount * n
        else:
            series[n - 1] = monthly_amount * (((1 + r) ** n - 1) / r) * (1 + r)
    return series


def total_invested(monthly_amount: float, months: int) -> np.ndarray:
    """Straight-line cumulative invested amount."""
    return np.arange(1, months + 1) * monthly_amount


# ══════════════════════════════════════════════════════════════════════════════
# 3. PRICING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def lookup_price(app_name: str) -> dict | None:
    key = app_name.strip().lower()
    return PRICING_DATABASE.get(key)


def scrape_price(app_name: str) -> dict | None:
    """Best-effort scrape — returns None on any failure."""
    if not SCRAPING_AVAILABLE:
        return None
    try:
        query = f"{app_name} subscription price India INR site:in"
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        # Look for ₹ price patterns
        import re
        text = soup.get_text()
        prices = re.findall(r"₹\s*(\d+(?:,\d+)?)", text)
        if prices:
            price_val = int(prices[0].replace(",", ""))
            if 10 <= price_val <= 10000:  # sanity range
                return {
                    "price": price_val,
                    "display": app_name.title(),
                    "category": "Other",
                    "source": "scraped",
                }
    except Exception:
        pass
    return None


def resolve_price(app_name: str) -> tuple[dict | None, str]:
    """Returns (data_dict, source_label)."""
    # 1. Exact / fuzzy match in database
    result = lookup_price(app_name)
    if result:
        return result, "database"

    # Fuzzy: check if any key contains the search term
    key = app_name.strip().lower()
    for db_key, val in PRICING_DATABASE.items():
        if key in db_key or db_key in key:
            return val, "database"

    # 2. Scrape fallback
    scraped = scrape_price(app_name)
    if scraped:
        return scraped, "scraped"

    return None, "not_found"


# ══════════════════════════════════════════════════════════════════════════════
# 4. EXCEL GENERATOR
# ══════════════════════════════════════════════════════════════════════════════

def generate_excel(subscriptions: list[dict]) -> bytes:
    """
    Build a formatted Excel workbook with:
    - Summary sheet: each subscription + SIP projections
    - Month-by-month detail sheet
    Uses xlsxwriter for native Excel formulas and formatting.
    """
    output = io.BytesIO()
    wb = pd.ExcelWriter(output, engine="xlsxwriter")  # noqa
    workbook = wb.book

    # ── Formats ──────────────────────────────────────────────────────────────
    fmt_title  = workbook.add_format({"bold": True, "font_size": 16, "font_color": "#FFFFFF", "bg_color": "#1A1A2E", "border": 0})
    fmt_header = workbook.add_format({"bold": True, "font_color": "#FFFFFF", "bg_color": "#16213E", "border": 1, "border_color": "#0F3460", "align": "center", "valign": "vcenter", "text_wrap": True})
    fmt_sub    = workbook.add_format({"bold": True, "font_color": "#E0E0E0", "bg_color": "#0F3460", "border": 1, "border_color": "#0F3460"})
    fmt_inr    = workbook.add_format({"num_format": '₹#,##0', "bg_color": "#1A1A2E", "font_color": "#E0E0E0", "border": 1, "border_color": "#2D2D44"})
    fmt_inr_eq = workbook.add_format({"num_format": '₹#,##0', "bg_color": "#1A1A2E", "font_color": "#FFB74D", "bold": True, "border": 1, "border_color": "#2D2D44"})
    fmt_pct    = workbook.add_format({"num_format": '0.0%', "bg_color": "#1A1A2E", "font_color": "#81C784", "border": 1, "border_color": "#2D2D44", "align": "center"})
    fmt_month  = workbook.add_format({"num_format": '0', "bg_color": "#1A1A2E", "font_color": "#9E9E9E", "border": 1, "border_color": "#2D2D44", "align": "center"})
    fmt_gap    = workbook.add_format({"num_format": '₹#,##0', "bg_color": "#0D2137", "font_color": "#E53935", "bold": True, "border": 1, "border_color": "#2D2D44"})

    # ── Sheet 1: Summary ─────────────────────────────────────────────────────
    ws = workbook.add_worksheet("Opportunity Cost Summary")
    ws.set_tab_color("#0F3460")
    ws.hide_gridlines(2)
    ws.set_zoom(100)

    # Title banner
    ws.merge_range("A1:L1", "📊 Subscription Opportunity Cost Calculator — India Edition", fmt_title)
    ws.set_row(0, 30)

    headers = [
        "Subscription", "Category", "Monthly Cost (₹)",
        "1Y — FD (6%)", "1Y — Debt (8%)", "1Y — Equity (12%)",
        "3Y — FD (6%)", "3Y — Debt (8%)", "3Y — Equity (12%)",
        "5Y — FD (6%)", "5Y — Debt (8%)", "5Y — Equity (12%)",
        "10Y — FD (6%)", "10Y — Debt (8%)", "10Y — Equity (12%)",
        "10Y Wealth Gap (Spent vs Equity)",
    ]
    col_widths = [22, 16, 18] + [16] * 12 + [28]
    ws.set_row(1, 36)
    for col, (h, w) in enumerate(zip(headers, col_widths)):
        ws.write(1, col, h, fmt_header)
        ws.set_column(col, col, w)

    # Rates and periods for formula cells
    periods = {
        "1Y":  (6,  8,  12),
        "3Y":  (36, 8,  12),
        "5Y":  (60, 8,  12),
        "10Y": (120, 8, 12),
    }

    for row_idx, sub in enumerate(subscriptions):
        data_row = row_idx + 2  # 0-indexed, row 0=title, row 1=header
        P = sub["price"]
        name = sub["display"]
        cat  = sub.get("category", "Other")

        ws.write(data_row, 0, name, fmt_sub)
        ws.write(data_row, 1, cat,  fmt_sub)
        ws.write(data_row, 2, P,    fmt_inr)

        col = 3
        for label, (n, _, _) in periods.items():
            for rate in [6.0, 8.0, 12.0]:
                fv = sip_future_value(P, rate, n)
                fmt = fmt_inr_eq if rate == 12.0 else fmt_inr
                ws.write(data_row, col, fv, fmt)
                col += 1

        # Wealth gap: total spent vs equity 10Y
        total_spent = P * 120
        equity_10y  = sip_future_value(P, 12.0, 120)
        gap         = equity_10y - total_spent
        ws.write(data_row, col, gap, fmt_gap)

    # Freeze panes
    ws.freeze_panes(2, 3)

    # ── Sheet 2: Monthly Detail ───────────────────────────────────────────────
    ws2 = workbook.add_worksheet("Monthly Growth Detail")
    ws2.set_tab_color("#16213E")
    ws2.hide_gridlines(2)

    if subscriptions:
        sub = subscriptions[0]  # Detail for first subscription
        P = sub["price"]
        name = sub["display"]

        ws2.merge_range("A1:F1", f"Monthly SIP Growth — {name} (₹{P:,}/mo)", fmt_title)
        ws2.set_row(0, 30)

        detail_headers = ["Month", "Total Invested (₹)", "FD Value (₹)", "Debt Fund Value (₹)", "Equity Fund Value (₹)", "Wealth Gap (₹)"]
        detail_widths  = [10, 20, 18, 20, 22, 18]
        ws2.set_row(1, 36)
        for c, (h, w) in enumerate(zip(detail_headers, detail_widths)):
            ws2.write(1, c, h, fmt_header)
            ws2.set_column(c, c, w)

        for month in range(1, HORIZON_MONTHS + 1):
            r = month + 1  # data starts row index 2
            invested = P * month
            fd_val   = sip_future_value(P, 6.0,  month)
            debt_val = sip_future_value(P, 8.0,  month)
            eq_val   = sip_future_value(P, 12.0, month)
            gap      = eq_val - invested

            ws2.write(r, 0, month,    fmt_month)
            ws2.write(r, 1, invested, fmt_inr)
            ws2.write(r, 2, fd_val,   fmt_inr)
            ws2.write(r, 3, debt_val, fmt_inr)
            ws2.write(r, 4, eq_val,   fmt_inr_eq)
            ws2.write(r, 5, gap,      fmt_gap)

        ws2.freeze_panes(2, 1)

    wb.close()
    output.seek(0)
    return output.read()


# ══════════════════════════════════════════════════════════════════════════════
# 5. STREAMLIT UI
# ══════════════════════════════════════════════════════════════════════════════

def format_inr(amount: float) -> str:
    """Format number as Indian Rupee string with commas."""
    if amount >= 1_00_00_000:
        return f"₹{amount / 1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"₹{amount / 1_00_000:.2f} L"
    elif amount >= 1_000:
        return f"₹{amount:,.0f}"
    return f"₹{amount:.0f}"


def render_metric_card(label: str, value: str, delta: str = "", icon: str = ""):
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #16213E 0%, #0F3460 100%);
            border: 1px solid #2D2D44;
            border-radius: 12px;
            padding: 18px 20px;
            text-align: center;
            margin-bottom: 8px;
        ">
            <div style="font-size: 24px; margin-bottom: 4px;">{icon}</div>
            <div style="font-size: 13px; color: #9E9E9E; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px;">{label}</div>
            <div style="font-size: 26px; font-weight: 700; color: #FFFFFF;">{value}</div>
            {"<div style='font-size:13px;color:#81C784;margin-top:4px;'>"+delta+"</div>" if delta else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_wealth_chart(subscriptions: list[dict]) -> go.Figure:
    months = np.arange(1, HORIZON_MONTHS + 1)
    fig = go.Figure()

    for sub in subscriptions:
        P = sub["price"]
        label = sub["display"]

        # Total invested (linear)
        invested = total_invested(P, HORIZON_MONTHS)
        fig.add_trace(go.Scatter(
            x=months, y=invested,
            name=f"{label} — Spent",
            line=dict(color="#546E7A", width=1.5, dash="dot"),
            hovertemplate="Month %{x}<br>Total Spent: ₹%{y:,.0f}<extra></extra>",
        ))

        for bm_name, bm in BENCHMARKS.items():
            series = build_growth_series(P, bm["rate"], HORIZON_MONTHS)
            fig.add_trace(go.Scatter(
                x=months, y=series,
                name=f"{label} — {bm_name}",
                line=dict(color=bm["color"], width=2.5),
                hovertemplate=f"Month %{{x}}<br>{bm_name}: ₹%{{y:,.0f}}<extra></extra>",
            ))

    fig.update_layout(
        paper_bgcolor="#0D1117",
        plot_bgcolor="#0D1117",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#E0E0E0"),
        title=dict(
            text="Wealth Gap — What Your Subscriptions Could Have Built",
            font=dict(size=18, color="#FFFFFF"),
            x=0.0, y=0.97,
        ),
        legend=dict(
            bgcolor="#16213E",
            bordercolor="#2D2D44",
            borderwidth=1,
            font=dict(size=11),
        ),
        xaxis=dict(
            title="Month",
            gridcolor="#1E1E2E",
            zeroline=False,
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            title="Value (₹)",
            gridcolor="#1E1E2E",
            zeroline=False,
            tickfont=dict(size=11),
            tickformat="₹,.0f",
        ),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=60, b=50),
        height=480,
    )
    return fig


def build_bar_comparison(subscriptions: list[dict]) -> go.Figure:
    """10-year FV bar chart per subscription per benchmark."""
    labels, fd_vals, debt_vals, eq_vals, spent_vals = [], [], [], [], []

    for sub in subscriptions:
        P = sub["price"]
        labels.append(sub["display"])
        fd_vals.append(sip_future_value(P, 6.0,  120))
        debt_vals.append(sip_future_value(P, 8.0,  120))
        eq_vals.append(sip_future_value(P, 12.0, 120))
        spent_vals.append(P * 120)

    fig = go.Figure(data=[
        go.Bar(name="Total Spent",       x=labels, y=spent_vals, marker_color="#546E7A",  text=[format_inr(v) for v in spent_vals],  textposition="auto"),
        go.Bar(name="FD (6%)",           x=labels, y=fd_vals,    marker_color="#4FC3F7",  text=[format_inr(v) for v in fd_vals],    textposition="auto"),
        go.Bar(name="Debt Fund (8%)",    x=labels, y=debt_vals,  marker_color="#81C784",  text=[format_inr(v) for v in debt_vals],  textposition="auto"),
        go.Bar(name="Equity Fund (12%)", x=labels, y=eq_vals,    marker_color="#FFB74D",  text=[format_inr(v) for v in eq_vals],   textposition="auto"),
    ])
    fig.update_layout(
        barmode="group",
        paper_bgcolor="#0D1117",
        plot_bgcolor="#0D1117",
        font=dict(family="Inter, Segoe UI, sans-serif", color="#E0E0E0"),
        title=dict(text="10-Year Projection Comparison", font=dict(size=16, color="#FFFFFF"), x=0.0),
        legend=dict(bgcolor="#16213E", bordercolor="#2D2D44", borderwidth=1),
        xaxis=dict(gridcolor="#1E1E2E"),
        yaxis=dict(gridcolor="#1E1E2E", tickformat="₹,.0f"),
        margin=dict(l=60, r=20, t=50, b=50),
        height=380,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# 6. MAIN APP
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Subscription Opportunity Cost — India",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # ── Global CSS ────────────────────────────────────────────────────────────
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', 'Segoe UI', sans-serif !important;
        }
        .stApp {
            background: #0D1117;
        }
        .block-container {
            padding-top: 1.5rem;
        }
        .stButton > button {
            background: linear-gradient(135deg, #0F3460 0%, #16213E 100%);
            color: #FFFFFF;
            border: 1px solid #4FC3F7;
            border-radius: 8px;
            font-weight: 600;
            letter-spacing: 0.03em;
            padding: 0.5rem 1.2rem;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #16213E 0%, #0F3460 100%);
            border-color: #FFB74D;
        }
        .stTextInput > div > div > input {
            background-color: #16213E;
            color: #FFFFFF;
            border: 1px solid #2D2D44;
            border-radius: 8px;
        }
        .stNumberInput > div > div > input {
            background-color: #16213E;
            color: #FFFFFF;
            border: 1px solid #2D2D44;
            border-radius: 8px;
        }
        .stSelectbox > div > div {
            background-color: #16213E;
            color: #FFFFFF;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem !important;
            color: #FFB74D !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #9E9E9E !important;
        }
        .stDataFrame { border-radius: 10px; }
        hr { border-color: #2D2D44; }
        .sidebar-info {
            background: #16213E;
            border-left: 3px solid #4FC3F7;
            border-radius: 0 8px 8px 0;
            padding: 10px 14px;
            margin: 8px 0;
            font-size: 13px;
            color: #B0BEC5;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ── Header ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #0F3460 0%, #1A1A2E 60%, #0D1117 100%);
            border-bottom: 1px solid #2D2D44;
            padding: 24px 32px 20px;
            margin: -1.5rem -4rem 1.5rem;
        ">
            <h1 style="color:#FFFFFF;margin:0;font-size:2rem;font-weight:700;letter-spacing:-0.02em;">
                📊 Subscription Opportunity Cost Calculator
            </h1>
            <p style="color:#78909C;margin:6px 0 0;font-size:1rem;">
                India Edition &nbsp;·&nbsp; Inspired by Sandeep Jethwani's Subscription Economy Analysis
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Session state ─────────────────────────────────────────────────────────
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []

    # ══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown("### ➕ Add Subscription")

        search_name = st.text_input(
            "Search App Name",
            placeholder="e.g. Netflix, Spotify, Swiggy One…",
            key="search_bar",
        )

        found_data = None
        found_source = ""
        manual_price = None

        if search_name:
            found_data, found_source = resolve_price(search_name)
            if found_data:
                st.success(f"✅ Found: **{found_data['display']}** — {found_source.title()}")
                st.markdown(
                    f"<div class='sidebar-info'>Category: <b>{found_data['category']}</b><br>"
                    f"Default Price: <b>₹{found_data['price']}</b>/month</div>",
                    unsafe_allow_html=True,
                )
                manual_price = st.number_input(
                    "Adjust Monthly Price (₹)",
                    min_value=1,
                    max_value=50000,
                    value=found_data["price"],
                    step=10,
                )
            else:
                st.warning("⚠️ Not in database. Enter price manually.")
                manual_price = st.number_input(
                    "Monthly Price (₹)",
                    min_value=1,
                    max_value=50000,
                    value=299,
                    step=10,
                )

        if st.button("Add to Portfolio", use_container_width=True):
            if search_name and manual_price:
                entry = {
                    "display":  found_data["display"]  if found_data else search_name.title(),
                    "category": found_data["category"] if found_data else "Other",
                    "price":    manual_price,
                    "source":   found_source or "manual",
                }
                # Avoid duplicates
                existing = [s["display"] for s in st.session_state.portfolio]
                if entry["display"] not in existing:
                    st.session_state.portfolio.append(entry)
                    st.rerun()
                else:
                    st.error("Already in portfolio!")
            else:
                st.error("Please enter an app name and price.")

        st.divider()
        st.markdown("### 📋 Quick Add")
        quick_apps = ["Netflix Standard", "Amazon Prime", "YouTube Premium",
                      "Spotify Premium", "Disney+ Hotstar", "Zomato Gold"]
        for app in quick_apps:
            if st.button(app, use_container_width=True, key=f"quick_{app}"):
                data, src = resolve_price(app)
                if data:
                    existing = [s["display"] for s in st.session_state.portfolio]
                    if data["display"] not in existing:
                        st.session_state.portfolio.append({**data, "source": src})
                        st.rerun()

        st.divider()
        st.markdown("### 🗑️ Portfolio")
        if st.session_state.portfolio:
            for i, sub in enumerate(st.session_state.portfolio):
                col1, col2 = st.columns([3, 1])
                col1.markdown(f"**{sub['display']}**  \n₹{sub['price']}/mo")
                if col2.button("✕", key=f"del_{i}"):
                    st.session_state.portfolio.pop(i)
                    st.rerun()
        else:
            st.markdown("<div class='sidebar-info'>No subscriptions added yet.</div>", unsafe_allow_html=True)

        st.divider()
        st.markdown("### ℹ️ Benchmarks")
        for bm_name, bm in BENCHMARKS.items():
            st.markdown(
                f"<div class='sidebar-info'>{bm['icon']} <b>{bm_name}</b></div>",
                unsafe_allow_html=True,
            )

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN PANEL
    # ══════════════════════════════════════════════════════════════════════════
    portfolio = st.session_state.portfolio

    if not portfolio:
        st.markdown(
            """
            <div style="
                text-align:center;
                padding: 80px 20px;
                color: #546E7A;
            ">
                <div style="font-size:64px;margin-bottom:16px;">💸</div>
                <h2 style="color:#78909C;font-weight:600;">Start by adding a subscription</h2>
                <p style="font-size:1rem;">Use the sidebar to search for apps like Netflix, Spotify, or Zomato Gold,<br>
                or click Quick Add to get started instantly.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    # ── Aggregate totals ──────────────────────────────────────────────────────
    total_monthly = sum(s["price"] for s in portfolio)
    total_spent_10y = total_monthly * 120
    fd_10y   = sip_future_value(total_monthly, 6.0,  120)
    debt_10y = sip_future_value(total_monthly, 8.0,  120)
    eq_10y   = sip_future_value(total_monthly, 12.0, 120)
    wealth_gap = eq_10y - total_spent_10y

    # ── KPI Cards ─────────────────────────────────────────────────────────────
    st.markdown("## 📈 Portfolio Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        render_metric_card("Monthly Burn", format_inr(total_monthly), icon="💳")
    with c2:
        render_metric_card("10Y Total Spent", format_inr(total_spent_10y), icon="🧾")
    with c3:
        render_metric_card("FD Value (6%)", format_inr(fd_10y), f"+{format_inr(fd_10y - total_spent_10y)}", "🏦")
    with c4:
        render_metric_card("Debt Fund (8%)", format_inr(debt_10y), f"+{format_inr(debt_10y - total_spent_10y)}", "📊")
    with c5:
        render_metric_card("Equity Fund (12%)", format_inr(eq_10y), f"+{format_inr(wealth_gap)}", "🚀")

    st.divider()

    # ── Wealth Gap Alert ──────────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1A0A0A 0%, #2D1010 100%);
            border: 1px solid #E53935;
            border-left: 5px solid #E53935;
            border-radius: 10px;
            padding: 18px 24px;
            margin-bottom: 24px;
        ">
            <span style="font-size:1.1rem;color:#EF9A9A;font-weight:600;">⚠️ Wealth Opportunity Lost</span><br>
            <span style="font-size:0.95rem;color:#9E9E9E;margin-top:4px;display:block;">
                By spending <b style="color:#EF9A9A;">{format_inr(total_monthly)}/month</b> on subscriptions instead of an
                equity SIP, you miss out on <b style="color:#FF5252;font-size:1.2rem;">{format_inr(wealth_gap)}</b>
                over 10 years (vs. ₹{format_inr(total_spent_10y)} total invested).
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Line Chart ────────────────────────────────────────────────────────────
    st.markdown("## 📉 Wealth Gap — 120 Month Timeline")
    st.plotly_chart(
        build_wealth_chart([{"display": "All Subscriptions", "price": total_monthly}]),
        use_container_width=True,
    )

    # ── Bar Chart ─────────────────────────────────────────────────────────────
    st.markdown("## 🏆 Per-Subscription 10-Year Comparison")
    st.plotly_chart(build_bar_comparison(portfolio), use_container_width=True)

    # ── Detailed Table ────────────────────────────────────────────────────────
    st.markdown("## 📊 Detailed Projection Table")

    rows = []
    for sub in portfolio:
        P = sub["price"]
        for bm_name, bm in BENCHMARKS.items():
            rows.append({
                "Subscription":   sub["display"],
                "Category":       sub["category"],
                "Monthly (₹)":    P,
                "Scenario":       bm_name,
                "1Y Value":       sip_future_value(P, bm["rate"], 12),
                "3Y Value":       sip_future_value(P, bm["rate"], 36),
                "5Y Value":       sip_future_value(P, bm["rate"], 60),
                "10Y Value":      sip_future_value(P, bm["rate"], 120),
                "10Y Wealth Gap": sip_future_value(P, bm["rate"], 120) - (P * 120),
            })

    df = pd.DataFrame(rows)

    # Format for display
    inr_cols = ["Monthly (₹)", "1Y Value", "3Y Value", "5Y Value", "10Y Value", "10Y Wealth Gap"]
    df_display = df.copy()
    for col in inr_cols:
        df_display[col] = df_display[col].apply(format_inr)

    st.dataframe(
        df_display,
        use_container_width=True,
        height=min(400, 60 + len(df_display) * 35),
        hide_index=True,
    )

    # ── Excel Download ────────────────────────────────────────────────────────
    st.divider()
    st.markdown("## 📥 Export to Excel")
    col_dl, col_info = st.columns([1, 3])
    with col_dl:
        if st.button("⬇️ Download Excel Report", use_container_width=True):
            with st.spinner("Generating Excel workbook…"):
                excel_bytes = generate_excel(portfolio)
            st.download_button(
                label="📄 Click to Save — Opportunity_Cost_Report.xlsx",
                data=excel_bytes,
                file_name="Subscription_Opportunity_Cost_India.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    with col_info:
        st.markdown(
            """
            <div class='sidebar-info' style='margin-top:8px;'>
            The Excel report includes:<br>
            • <b>Summary sheet</b> — all subscriptions × all scenarios × 1/3/5/10Y projections<br>
            • <b>Monthly detail sheet</b> — 120-month compounding breakdown for your first subscription<br>
            • Dark-themed professional formatting with INR currency
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Assumptions Footer ────────────────────────────────────────────────────
    st.divider()
    st.markdown(
        """
        <div style="color:#546E7A;font-size:12px;text-align:center;padding:12px 0 4px;">
        <b>Assumptions & Disclaimers:</b> · Formula: FV = P × [((1+r)ⁿ − 1) / r] × (1+r) &nbsp;·&nbsp;
        Monthly compounding (SIP-style) &nbsp;·&nbsp; Returns: FD 6%, Debt Fund 8%, Equity/Index Fund 12% p.a. &nbsp;·&nbsp;
        Past returns do not guarantee future performance. &nbsp;·&nbsp;
        For educational purposes only. Consult a SEBI-registered advisor before investing.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
