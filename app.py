"""
Subscription Opportunity Cost Calculator — India Edition  (Enhanced)
=====================================================================
Premium Streamlit app: SIP projections, wealth gap analytics, 6 chart types,
animated totals, and styled Excel export.
"""

import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

# ══════════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

PRICING_DATABASE = {
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
    "notion plus":          {"price": 330,  "display": "Notion Plus",              "category": "Productivity"},
    "notion":               {"price": 330,  "display": "Notion Plus",              "category": "Productivity"},
    "canva pro":            {"price": 499,  "display": "Canva Pro",                "category": "Productivity"},
    "canva":                {"price": 499,  "display": "Canva Pro",                "category": "Productivity"},
    "grammarly premium":    {"price": 1000, "display": "Grammarly Premium",        "category": "Productivity"},
    "grammarly":            {"price": 1000, "display": "Grammarly Premium",        "category": "Productivity"},
    "gpay":                 {"price": 0,    "display": "Google Pay (Free)",         "category": "Finance"},
    "zerodha":              {"price": 0,    "display": "Zerodha (Free)",            "category": "Finance"},
    "groww":                {"price": 0,    "display": "Groww (Free)",              "category": "Finance"},
}

BENCHMARKS = {
    "FD (6% p.a.)":           {"rate": 6.0,  "color": "#4FC3F7", "fill": "rgba(79,195,247,0.12)",  "icon": "🏦"},
    "Debt Fund (8% p.a.)":    {"rate": 8.0,  "color": "#A5D6A7", "fill": "rgba(165,214,167,0.12)", "icon": "📊"},
    "Equity Fund (12% p.a.)": {"rate": 12.0, "color": "#FFB74D", "fill": "rgba(255,183,77,0.15)",  "icon": "🚀"},
}

HORIZON_MONTHS = 120

CATEGORY_COLORS = {
    "Entertainment":  "#7B61FF",
    "Food & Delivery":"#FF6B6B",
    "Music":          "#4FC3F7",
    "Productivity":   "#81C784",
    "Professional":   "#FFB74D",
    "Storage":        "#F06292",
    "Health & Fitness":"#80CBC4",
    "Education":      "#FFD54F",
    "Finance":        "#90A4AE",
    "Other":          "#B0BEC5",
}

DARK = {
    "bg":       "#0A0E1A",
    "surface":  "#0F1629",
    "card":     "#141C35",
    "border":   "#1E2D50",
    "text":     "#E8EAF0",
    "muted":    "#6B7A99",
    "accent":   "#4FC3F7",
    "gold":     "#FFB74D",
    "green":    "#A5D6A7",
    "red":      "#EF5350",
}

# ══════════════════════════════════════════════════════════════════════════════
# MATH
# ══════════════════════════════════════════════════════════════════════════════

def sip_fv(P: float, annual_pct: float, months: int) -> float:
    if P == 0:
        return 0.0
    if annual_pct == 0:
        return round(P * months, 2)
    r = annual_pct / 12 / 100
    return round(P * (((1 + r) ** months - 1) / r) * (1 + r), 2)


def growth_series(P: float, annual_pct: float, months: int) -> np.ndarray:
    if P == 0:
        return np.zeros(months)
    r = annual_pct / 12 / 100
    n = np.arange(1, months + 1)
    if annual_pct == 0:
        return P * n
    return P * (((1 + r) ** n - 1) / r) * (1 + r)


def invested_series(P: float, months: int) -> np.ndarray:
    return P * np.arange(1, months + 1)


# ══════════════════════════════════════════════════════════════════════════════
# PRICING ENGINE
# ══════════════════════════════════════════════════════════════════════════════

def resolve_price(name: str):
    key = name.strip().lower()
    if key in PRICING_DATABASE:
        return PRICING_DATABASE[key], "database"
    for k, v in PRICING_DATABASE.items():
        if key in k or k in key:
            return v, "database"
    if SCRAPING_AVAILABLE:
        try:
            import re
            headers = {"User-Agent": "Mozilla/5.0"}
            url = f"https://www.google.com/search?q={name.replace(' ', '+')}+subscription+price+India+INR"
            resp = requests.get(url, headers=headers, timeout=5)
            text = BeautifulSoup(resp.text, "html.parser").get_text()
            prices = re.findall(r"[\u20b9]\s*(\d+(?:,\d+)?)", text)
            if prices:
                val = int(prices[0].replace(",", ""))
                if 10 <= val <= 10000:
                    return {"price": val, "display": name.title(), "category": "Other"}, "scraped"
        except Exception:
            pass
    return None, "not_found"


# ══════════════════════════════════════════════════════════════════════════════
# FORMATTING
# ══════════════════════════════════════════════════════════════════════════════

def fmt_inr(amount: float, short: bool = False) -> str:
    if short:
        if abs(amount) >= 1_00_00_000:
            return f"\u20b9{amount/1_00_00_000:.2f} Cr"
        if abs(amount) >= 1_00_000:
            return f"\u20b9{amount/1_00_000:.2f} L"
        if abs(amount) >= 1_000:
            return f"\u20b9{amount/1_000:.1f}K"
        return f"\u20b9{amount:.0f}"
    if abs(amount) >= 1_00_00_000:
        return f"\u20b9{amount/1_00_00_000:.2f} Cr"
    if abs(amount) >= 1_00_000:
        return f"\u20b9{amount/1_00_000:.2f} L"
    return f"\u20b9{amount:,.0f}"


# ══════════════════════════════════════════════════════════════════════════════
# CHART BUILDERS
# ══════════════════════════════════════════════════════════════════════════════

def _dark_layout(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    fig.update_layout(
        paper_bgcolor=DARK["bg"],
        plot_bgcolor=DARK["surface"],
        font=dict(family="Inter, Segoe UI, sans-serif", color=DARK["text"], size=12),
        title=dict(text=title, font=dict(size=15, color="#FFFFFF"), x=0.0, y=0.97, xanchor="left"),
        legend=dict(bgcolor=DARK["card"], bordercolor=DARK["border"], borderwidth=1,
                    font=dict(size=11), orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(l=60, r=20, t=55, b=50),
        height=height,
        xaxis=dict(gridcolor=DARK["border"], zeroline=False, tickfont=dict(size=11)),
        yaxis=dict(gridcolor=DARK["border"], zeroline=False, tickfont=dict(size=11)),
    )
    return fig


def chart_wealth_gap(P: float) -> go.Figure:
    """Filled area line chart — main hero chart."""
    months = np.arange(1, HORIZON_MONTHS + 1)
    invested = invested_series(P, HORIZON_MONTHS)

    fig = go.Figure()

    # Invested baseline (filled)
    fig.add_trace(go.Scatter(
        x=months, y=invested,
        name="Total Spent",
        line=dict(color="#546E7A", width=2, dash="dot"),
        fill="tozeroy",
        fillcolor="rgba(84,110,122,0.08)",
        hovertemplate="Month %{x}<br>Spent: \u20b9%{y:,.0f}<extra></extra>",
    ))

    # Each benchmark with fill-to-previous
    prev_fill = "tozeroy"
    for i, (bm_name, bm) in enumerate(BENCHMARKS.items()):
        s = growth_series(P, bm["rate"], HORIZON_MONTHS)
        fig.add_trace(go.Scatter(
            x=months, y=s,
            name=bm_name,
            line=dict(color=bm["color"], width=2.5),
            fill="tonexty" if i == 0 else "tonexty",
            fillcolor=bm["fill"],
            hovertemplate=f"Month %{{x}}<br>{bm_name}: \u20b9%{{y:,.0f}}<extra></extra>",
        ))

    # Milestone annotations at 3Y, 5Y, 10Y
    for mo, label in [(36, "3Y"), (60, "5Y"), (120, "10Y")]:
        eq_val = growth_series(P, 12.0, HORIZON_MONTHS)[mo - 1]
        fig.add_vline(x=mo, line=dict(color=DARK["border"], width=1, dash="dash"))
        fig.add_annotation(x=mo, y=eq_val, text=f"<b>{label}</b><br>{fmt_inr(eq_val, short=True)}",
                           showarrow=False, yshift=18,
                           font=dict(size=10, color=DARK["gold"]),
                           bgcolor=DARK["card"], borderpad=4)

    fig.update_layout(hovermode="x unified")
    _dark_layout(fig, "Wealth Gap — Subscription Spend vs SIP Returns (120 Months)", height=460)
    fig.update_yaxes(tickprefix="\u20b9", tickformat=",")
    fig.update_xaxes(title_text="Month Number")
    fig.update_yaxes(title_text="Portfolio Value (INR)")
    return fig


def chart_bar_comparison(portfolio: list) -> go.Figure:
    """Grouped horizontal bar chart — per subscription, per benchmark."""
    labels = [s["display"] for s in portfolio]
    categories = ["Total Spent", "FD (6%)", "Debt (8%)", "Equity (12%)"]
    colors = ["#546E7A", "#4FC3F7", "#A5D6A7", "#FFB74D"]

    fig = go.Figure()
    data_map = {
        "Total Spent": [s["price"] * 120 for s in portfolio],
        "FD (6%)":     [sip_fv(s["price"], 6.0,  120) for s in portfolio],
        "Debt (8%)":   [sip_fv(s["price"], 8.0,  120) for s in portfolio],
        "Equity (12%)":[sip_fv(s["price"], 12.0, 120) for s in portfolio],
    }

    for cat, col in zip(categories, colors):
        vals = data_map[cat]
        fig.add_trace(go.Bar(
            name=cat, y=labels, x=vals,
            orientation="h",
            marker=dict(color=col, line=dict(width=0)),
            text=[fmt_inr(v, short=True) for v in vals],
            textposition="outside",
            textfont=dict(size=10, color="#FFFFFF"),
            hovertemplate=f"{cat}: \u20b9%{{x:,.0f}}<extra></extra>",
        ))

    fig.update_layout(barmode="group")
    _dark_layout(fig, "10-Year SIP Projection — Per Subscription", height=max(380, 100 + len(portfolio) * 60))
    fig.update_xaxes(title_text="Value after 10 Years (INR)", tickprefix="\u20b9", tickformat=",")
    fig.update_yaxes(title_text="")
    return fig


def chart_donut_category(portfolio: list) -> go.Figure:
    """Donut chart — monthly spend by category."""
    cat_totals: dict[str, float] = {}
    for s in portfolio:
        cat_totals[s["category"]] = cat_totals.get(s["category"], 0) + s["price"]

    labels = list(cat_totals.keys())
    values = list(cat_totals.values())
    colors = [CATEGORY_COLORS.get(l, "#B0BEC5") for l in labels]

    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        hole=0.62,
        marker=dict(colors=colors, line=dict(color=DARK["bg"], width=2)),
        textinfo="percent+label",
        textfont=dict(size=11),
        hovertemplate="%{label}<br>\u20b9%{value:,.0f}/mo (%{percent})<extra></extra>",
        pull=[0.04 if v == max(values) else 0 for v in values],
    ))

    total_mo = sum(values)
    fig.add_annotation(text=f"<b>{fmt_inr(total_mo)}</b><br><span style='font-size:11px'>per month</span>",
                       x=0.5, y=0.5, showarrow=False,
                       font=dict(size=16, color="#FFFFFF"))

    _dark_layout(fig, "Monthly Spend by Category", height=380)
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02,
                    bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=20, r=120, t=50, b=20),
    )
    return fig


def chart_waterfall_total(portfolio: list) -> go.Figure:
    """Waterfall chart — each subscription's contribution to total monthly burn."""
    subs = sorted(portfolio, key=lambda s: s["price"], reverse=True)
    names = [s["display"] for s in subs]
    prices = [s["price"] for s in subs]
    total = sum(prices)

    measure = ["relative"] * len(names) + ["total"]
    x = names + ["TOTAL"]
    y = prices + [0]

    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=measure,
        x=x,
        y=y,
        connector=dict(line=dict(color=DARK["border"], width=1)),
        increasing=dict(marker=dict(color="#4FC3F7")),
        totals=dict(marker=dict(color=DARK["gold"])),
        text=[f"\u20b9{p:,}" for p in prices] + [f"\u20b9{total:,}"],
        textposition="outside",
        textfont=dict(size=11, color="#FFFFFF"),
        hovertemplate="%{x}<br>\u20b9%{y:,.0f}<extra></extra>",
    ))

    _dark_layout(fig, "Monthly Burn Breakdown — Waterfall", height=380)
    fig.update_yaxes(title_text="Monthly Cost (INR)", tickprefix="\u20b9", tickformat=",")
    return fig


def chart_milestone_radar(P: float) -> go.Figure:
    """Radar / spider chart — FV at 1Y, 3Y, 5Y, 10Y for each benchmark."""
    horizons = [12, 36, 60, 120]
    labels   = ["1 Year", "3 Years", "5 Years", "10 Years"]

    fig = go.Figure()
    for bm_name, bm in BENCHMARKS.items():
        vals = [sip_fv(P, bm["rate"], h) for h in horizons]
        vals_closed = vals + [vals[0]]
        labels_closed = labels + [labels[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals_closed,
            theta=labels_closed,
            name=bm_name,
            line=dict(color=bm["color"], width=2),
            fill="toself",
            fillcolor=bm["fill"],
            hovertemplate="%{theta}: \u20b9%{r:,.0f}<extra></extra>",
        ))

    fig.update_layout(
        polar=dict(
            bgcolor=DARK["surface"],
            radialaxis=dict(
                visible=True,
                gridcolor=DARK["border"],
                tickfont=dict(size=9, color=DARK["muted"]),
                tickprefix="\u20b9",
                tickformat=",",
            ),
            angularaxis=dict(gridcolor=DARK["border"], tickfont=dict(size=11)),
        ),
        paper_bgcolor=DARK["bg"],
        font=dict(family="Inter, Segoe UI, sans-serif", color=DARK["text"]),
        title=dict(text="Investment Horizon Radar", font=dict(size=15, color="#FFFFFF"), x=0.0),
        legend=dict(bgcolor=DARK["card"], bordercolor=DARK["border"], borderwidth=1,
                    font=dict(size=11), orientation="h", yanchor="bottom", y=-0.15, x=0.1),
        margin=dict(l=40, r=40, t=60, b=60),
        height=400,
    )
    return fig


def chart_yearly_growth_heatmap(portfolio: list) -> go.Figure:
    """Heatmap — equity FV per subscription across yearly milestones."""
    years = [1, 2, 3, 5, 7, 10]
    names = [s["display"] for s in portfolio]
    z = []
    for s in portfolio:
        row = [sip_fv(s["price"], 12.0, y * 12) for y in years]
        z.append(row)

    text_vals = [[fmt_inr(v, short=True) for v in row] for row in z]

    fig = go.Figure(go.Heatmap(
        z=z,
        x=[f"Year {y}" for y in years],
        y=names,
        text=text_vals,
        texttemplate="%{text}",
        colorscale=[
            [0.0,  "#0F1629"],
            [0.25, "#0F3460"],
            [0.5,  "#1565C0"],
            [0.75, "#F57F17"],
            [1.0,  "#FFB74D"],
        ],
        hovertemplate="%{y}<br>%{x}: \u20b9%{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(
            title="Value (INR)",
            tickfont=dict(color=DARK["muted"]),
            title_font=dict(color=DARK["muted"]),
            bgcolor=DARK["card"],
            bordercolor=DARK["border"],
        ),
    ))

    _dark_layout(fig, "Equity SIP Growth Heatmap (12% p.a.) — All Subscriptions",
                 height=max(300, 160 + len(portfolio) * 50))
    fig.update_xaxes(side="top")
    return fig


def chart_break_even(portfolio: list) -> go.Figure:
    """Line chart showing break-even month where SIP > total spent."""
    months = np.arange(1, HORIZON_MONTHS + 1)
    P = sum(s["price"] for s in portfolio)
    invested = invested_series(P, HORIZON_MONTHS)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=invested,
        name="Total Spent",
        line=dict(color="#546E7A", width=2, dash="dot"),
        hovertemplate="Month %{x}: Spent \u20b9%{y:,.0f}<extra></extra>",
    ))

    for bm_name, bm in BENCHMARKS.items():
        s = growth_series(P, bm["rate"], HORIZON_MONTHS)
        # Find break-even
        crossover = None
        for i, (sp, inv) in enumerate(zip(s, invested)):
            if sp >= inv:
                crossover = i + 1
                break

        fig.add_trace(go.Scatter(
            x=months, y=s,
            name=bm_name,
            line=dict(color=bm["color"], width=2.5),
            hovertemplate=f"{bm_name} Month %{{x}}: \u20b9%{{y:,.0f}}<extra></extra>",
        ))

        if crossover:
            fig.add_annotation(
                x=crossover, y=s[crossover - 1],
                text=f"Break-even<br>Month {crossover}",
                showarrow=True, arrowhead=2, arrowcolor=bm["color"],
                font=dict(size=9, color=bm["color"]),
                bgcolor=DARK["card"], borderpad=3, ax=30, ay=-30,
            )

    _dark_layout(fig, "Break-Even Analysis — When Does SIP Outpace Spend?", height=420)
    fig.update_layout(hovermode="x unified")
    fig.update_yaxes(title_text="Value (INR)", tickprefix="\u20b9", tickformat=",")
    fig.update_xaxes(title_text="Month")
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# EXCEL EXPORT
# ══════════════════════════════════════════════════════════════════════════════

def generate_excel(portfolio: list) -> bytes:
    out = io.BytesIO()
    wb_writer = pd.ExcelWriter(out, engine="xlsxwriter")
    wb = wb_writer.book

    # ── Formats ──────────────────────────────────────────────────────────────
    def F(**kw):
        return wb.add_format(kw)

    f_title  = F(bold=True, font_size=16, font_color="#FFFFFF", bg_color="#0A0E1A", border=0)
    f_head   = F(bold=True, font_color="#FFFFFF", bg_color="#141C35", border=1,
                 border_color="#1E2D50", align="center", valign="vcenter", text_wrap=True)
    f_sub    = F(bold=True, font_color="#E8EAF0", bg_color="#0F1629", border=1, border_color="#1E2D50")
    f_cat    = F(italic=True, font_color="#6B7A99", bg_color="#0F1629", border=1, border_color="#1E2D50")
    f_inr    = F(num_format="\u20b9#,##0", bg_color="#0F1629", font_color="#E8EAF0",
                 border=1, border_color="#1E2D50")
    f_gold   = F(num_format="\u20b9#,##0", bg_color="#0F1629", font_color="#FFB74D",
                 bold=True, border=1, border_color="#1E2D50")
    f_green  = F(num_format="\u20b9#,##0", bg_color="#0F1629", font_color="#A5D6A7",
                 border=1, border_color="#1E2D50")
    f_red    = F(num_format="\u20b9#,##0", bg_color="#0F1629", font_color="#EF9A9A",
                 bold=True, border=1, border_color="#1E2D50")
    f_mo     = F(num_format="0", bg_color="#0F1629", font_color="#6B7A99",
                 border=1, border_color="#1E2D50", align="center")
    f_total  = F(bold=True, font_size=12, font_color="#FFB74D", bg_color="#141C35",
                 border=2, border_color="#4FC3F7", num_format="\u20b9#,##0")
    f_tlabel = F(bold=True, font_size=12, font_color="#4FC3F7", bg_color="#141C35",
                 border=2, border_color="#4FC3F7")

    # ── Sheet 1: Summary ─────────────────────────────────────────────────────
    ws = wb.add_worksheet("Opportunity Cost Summary")
    ws.set_tab_color("#4FC3F7")
    ws.hide_gridlines(2)

    ws.merge_range("A1:P1", "  Subscription Opportunity Cost Calculator — India Edition", f_title)
    ws.set_row(0, 32)

    headers = [
        "Subscription", "Category", "Monthly (INR)",
        "1Y — FD (6%)", "1Y — Debt (8%)", "1Y — Equity (12%)",
        "3Y — FD (6%)", "3Y — Debt (8%)", "3Y — Equity (12%)",
        "5Y — FD (6%)", "5Y — Debt (8%)", "5Y — Equity (12%)",
        "10Y — FD (6%)", "10Y — Debt (8%)", "10Y — Equity (12%)",
        "10Y Wealth Gap",
    ]
    widths = [24, 16, 15] + [16] * 12 + [18]
    ws.set_row(1, 38)
    for c, (h, w) in enumerate(zip(headers, widths)):
        ws.write(1, c, h, f_head)
        ws.set_column(c, c, w)

    for ri, sub in enumerate(portfolio):
        dr = ri + 2
        P = sub["price"]
        ws.write(dr, 0, sub["display"],    f_sub)
        ws.write(dr, 1, sub["category"],   f_cat)
        ws.write(dr, 2, P,                 f_inr)
        col = 3
        for n in [12, 36, 60, 120]:
            for rate, fmt in [(6.0, f_green), (8.0, f_inr), (12.0, f_gold)]:
                ws.write(dr, col, sip_fv(P, rate, n), fmt)
                col += 1
        ws.write(dr, col, sip_fv(P, 12.0, 120) - P * 120, f_red)

    # Totals row
    tr = len(portfolio) + 2
    ws.set_row(tr, 30)
    ws.write(tr, 0, "TOTAL", f_tlabel)
    ws.write(tr, 1, "", f_tlabel)
    total_monthly = sum(s["price"] for s in portfolio)
    ws.write(tr, 2, total_monthly, f_total)
    col = 3
    for n in [12, 36, 60, 120]:
        for rate in [6.0, 8.0, 12.0]:
            ws.write(tr, col, sip_fv(total_monthly, rate, n), f_total)
            col += 1
    ws.write(tr, col, sip_fv(total_monthly, 12.0, 120) - total_monthly * 120, f_total)

    ws.freeze_panes(2, 3)

    # ── Sheet 2: Monthly Detail ───────────────────────────────────────────────
    ws2 = wb.add_worksheet("Monthly Growth Detail")
    ws2.set_tab_color("#FFB74D")
    ws2.hide_gridlines(2)

    total_P = sum(s["price"] for s in portfolio)
    ws2.merge_range("A1:F1", f"  Portfolio Monthly SIP Growth — INR {total_P:,}/month combined", f_title)
    ws2.set_row(0, 32)

    dh = ["Month", "Total Invested", "FD Value (6%)", "Debt Value (8%)", "Equity Value (12%)", "Wealth Gap"]
    dw = [10, 18, 18, 18, 20, 18]
    ws2.set_row(1, 36)
    for c, (h, w) in enumerate(zip(dh, dw)):
        ws2.write(1, c, h, f_head)
        ws2.set_column(c, c, w)

    for mo in range(1, HORIZON_MONTHS + 1):
        r = mo + 1
        inv = total_P * mo
        fd  = sip_fv(total_P, 6.0,  mo)
        dbt = sip_fv(total_P, 8.0,  mo)
        eq  = sip_fv(total_P, 12.0, mo)
        ws2.write(r, 0, mo,       f_mo)
        ws2.write(r, 1, inv,      f_inr)
        ws2.write(r, 2, fd,       f_green)
        ws2.write(r, 3, dbt,      f_inr)
        ws2.write(r, 4, eq,       f_gold)
        ws2.write(r, 5, eq - inv, f_red)

    ws2.freeze_panes(2, 1)

    wb_writer.close()
    out.seek(0)
    return out.read()


# ══════════════════════════════════════════════════════════════════════════════
# UI COMPONENTS
# ══════════════════════════════════════════════════════════════════════════════

CARD_CSS = f"""
background: linear-gradient(145deg, {DARK['card']} 0%, {DARK['surface']} 100%);
border: 1px solid {DARK['border']};
border-radius: 14px;
padding: 20px 18px;
text-align: center;
"""

def kpi_card(label: str, value: str, delta: str = "", icon: str = "",
             accent: str = "#FFFFFF", delta_color: str = "#A5D6A7"):
    delta_html = (
        f"<div style='font-size:12px;color:{delta_color};margin-top:4px;font-weight:500;'>{delta}</div>"
        if delta else ""
    )
    st.markdown(
        f"""<div style="{CARD_CSS}">
            <div style="font-size:22px;margin-bottom:2px;">{icon}</div>
            <div style="font-size:11px;color:{DARK['muted']};text-transform:uppercase;
                        letter-spacing:0.1em;margin-bottom:6px;">{label}</div>
            <div style="font-size:22px;font-weight:700;color:{accent};line-height:1.2;">{value}</div>
            {delta_html}
        </div>""",
        unsafe_allow_html=True,
    )


def section_header(text: str, sub: str = ""):
    sub_html = f"<p style='color:{DARK['muted']};font-size:13px;margin:2px 0 0;'>{sub}</p>" if sub else ""
    st.markdown(
        f"""<div style="margin: 28px 0 14px;">
            <h2 style="color:#FFFFFF;font-size:1.25rem;font-weight:700;margin:0;letter-spacing:-0.01em;">{text}</h2>
            {sub_html}
        </div>""",
        unsafe_allow_html=True,
    )


def info_box(html: str, border_color: str = DARK["accent"]):
    st.markdown(
        f"""<div style="background:{DARK['card']};border-left:4px solid {border_color};
            border-radius:0 10px 10px 0;padding:14px 18px;margin:8px 0;
            font-size:13px;color:{DARK['text']};">{html}</div>""",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# TOTALS PANEL
# ══════════════════════════════════════════════════════════════════════════════

def render_totals_panel(portfolio: list):
    total_mo = sum(s["price"] for s in portfolio)
    total_10y_spent = total_mo * 120
    fd_10y   = sip_fv(total_mo, 6.0,  120)
    debt_10y = sip_fv(total_mo, 8.0,  120)
    eq_10y   = sip_fv(total_mo, 12.0, 120)
    gap_fd   = fd_10y   - total_10y_spent
    gap_debt = debt_10y - total_10y_spent
    gap_eq   = eq_10y   - total_10y_spent
    annual_mo = total_mo * 12

    # Big totals strip
    st.markdown(
        f"""
        <div style="background:linear-gradient(135deg,#0F1629 0%,#141C35 50%,#0A1628 100%);
                    border:1px solid {DARK['border']};border-radius:16px;padding:28px 32px;margin:4px 0 20px;">
          <div style="font-size:12px;color:{DARK['muted']};text-transform:uppercase;letter-spacing:.12em;margin-bottom:12px;">
            Portfolio Total — {len(portfolio)} subscription{'s' if len(portfolio)!=1 else ''}
          </div>
          <div style="display:flex;flex-wrap:wrap;gap:32px;align-items:flex-end;">
            <div>
              <div style="font-size:13px;color:{DARK['muted']};">Monthly Burn</div>
              <div style="font-size:2.8rem;font-weight:800;color:#FFFFFF;line-height:1.1;">{fmt_inr(total_mo)}</div>
              <div style="font-size:13px;color:{DARK['muted']};margin-top:2px;">= {fmt_inr(annual_mo)} / year</div>
            </div>
            <div style="width:1px;background:{DARK['border']};height:70px;"></div>
            <div>
              <div style="font-size:13px;color:{DARK['muted']};">10-Year Spend</div>
              <div style="font-size:1.9rem;font-weight:700;color:#EF9A9A;line-height:1.1;">{fmt_inr(total_10y_spent)}</div>
              <div style="font-size:13px;color:{DARK['muted']};margin-top:2px;">if invested in nothing</div>
            </div>
            <div style="width:1px;background:{DARK['border']};height:70px;"></div>
            <div>
              <div style="font-size:13px;color:{DARK['muted']};">FD Opportunity (6%)</div>
              <div style="font-size:1.9rem;font-weight:700;color:{DARK['accent']};line-height:1.1;">{fmt_inr(fd_10y)}</div>
              <div style="font-size:13px;color:{DARK['accent']};margin-top:2px;">+{fmt_inr(gap_fd)} gain</div>
            </div>
            <div style="width:1px;background:{DARK['border']};height:70px;"></div>
            <div>
              <div style="font-size:13px;color:{DARK['muted']};">Debt Fund (8%)</div>
              <div style="font-size:1.9rem;font-weight:700;color:{DARK['green']};line-height:1.1;">{fmt_inr(debt_10y)}</div>
              <div style="font-size:13px;color:{DARK['green']};margin-top:2px;">+{fmt_inr(gap_debt)} gain</div>
            </div>
            <div style="width:1px;background:{DARK['border']};height:70px;"></div>
            <div>
              <div style="font-size:13px;color:{DARK['muted']};">Equity SIP (12%)</div>
              <div style="font-size:2.2rem;font-weight:800;color:{DARK['gold']};line-height:1.1;">{fmt_inr(eq_10y)}</div>
              <div style="font-size:13px;color:{DARK['gold']};margin-top:2px;">+{fmt_inr(gap_eq)} wealth created</div>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ROI % cards
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        kpi_card("Subscriptions", str(len(portfolio)), icon="📱", accent=DARK["accent"])
    with c2:
        kpi_card("Daily Cost", fmt_inr(total_mo / 30), icon="📅", accent=DARK["muted"])
    with c3:
        kpi_card("Annual Burn", fmt_inr(annual_mo), icon="🔥", accent="#EF9A9A", delta_color="#EF9A9A")
    with c4:
        roi_fd = (fd_10y / total_10y_spent - 1) * 100
        kpi_card("FD Return", f"{roi_fd:.1f}%", f"{fmt_inr(gap_fd)} gain", "🏦", DARK["accent"])
    with c5:
        roi_eq = (eq_10y / total_10y_spent - 1) * 100
        kpi_card("Equity Return", f"{roi_eq:.1f}%", f"{fmt_inr(gap_eq)} gain", "🚀", DARK["gold"])
    with c6:
        # Biggest single sub
        biggest = max(portfolio, key=lambda s: s["price"])
        kpi_card("Top Spend", fmt_inr(biggest["price"]), biggest["display"], "👑", "#F06292")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Subscription Opportunity Cost — India",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', 'Segoe UI', sans-serif !important;
    }}
    .stApp {{ background: {DARK['bg']}; }}
    section[data-testid="stSidebar"] > div {{
        background: {DARK['surface']};
        border-right: 1px solid {DARK['border']};
    }}
    .block-container {{ padding-top: 0 !important; max-width: 1400px; }}
    .stButton > button {{
        background: linear-gradient(135deg, {DARK['surface']} 0%, {DARK['card']} 100%);
        color: {DARK['text']};
        border: 1px solid {DARK['border']};
        border-radius: 8px;
        font-weight: 500;
        font-size: 13px;
        padding: 0.45rem 1rem;
        transition: all 0.18s ease;
        width: 100%;
    }}
    .stButton > button:hover {{
        border-color: {DARK['accent']};
        color: {DARK['accent']};
        background: {DARK['card']};
    }}
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input {{
        background: {DARK['card']} !important;
        color: {DARK['text']} !important;
        border: 1px solid {DARK['border']} !important;
        border-radius: 8px !important;
        font-size: 13px !important;
    }}
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {{
        border-color: {DARK['accent']} !important;
        box-shadow: 0 0 0 2px rgba(79,195,247,0.15) !important;
    }}
    .stSelectbox > div > div {{
        background: {DARK['card']};
        border: 1px solid {DARK['border']};
        border-radius: 8px;
    }}
    .stDataFrame {{ border-radius: 12px; overflow: hidden; }}
    .stDataFrame thead th {{
        background: {DARK['card']} !important;
        color: {DARK['muted']} !important;
        font-size: 11px !important;
        text-transform: uppercase;
        letter-spacing: .06em;
    }}
    hr {{ border-color: {DARK['border']}; margin: 20px 0; }}
    .stTabs [data-baseweb="tab-list"] {{
        background: {DARK['surface']};
        border-radius: 10px;
        gap: 4px;
        padding: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent;
        color: {DARK['muted']};
        border-radius: 7px;
        font-size: 13px;
        font-weight: 500;
        padding: 6px 16px;
    }}
    .stTabs [aria-selected="true"] {{
        background: {DARK['card']} !important;
        color: {DARK['accent']} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    # ── Hero header ───────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{DARK['surface']} 0%,{DARK['bg']} 100%);
                border-bottom:1px solid {DARK['border']};
                padding:28px 36px 22px;margin:-1px -4rem 0;position:relative;overflow:hidden;">
        <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
                    background:radial-gradient(circle,rgba(79,195,247,.12) 0%,transparent 70%);
                    border-radius:50%;"></div>
        <div style="position:absolute;bottom:-60px;left:30%;width:300px;height:300px;
                    background:radial-gradient(circle,rgba(255,183,77,.06) 0%,transparent 70%);
                    border-radius:50%;"></div>
        <span style="display:inline-block;background:{DARK['card']};border:1px solid {DARK['border']};
                     border-radius:20px;padding:3px 12px;font-size:11px;color:{DARK['accent']};
                     font-weight:600;letter-spacing:.08em;margin-bottom:10px;">
            INDIA EDITION
        </span>
        <h1 style="color:#FFFFFF;margin:0;font-size:2.2rem;font-weight:800;letter-spacing:-.03em;line-height:1.1;">
            Subscription Opportunity Cost
        </h1>
        <p style="color:{DARK['muted']};margin:8px 0 0;font-size:14px;">
            Visualize the true wealth cost of your monthly subscriptions vs. SIP returns in FD, Debt, and Equity funds.
            &nbsp;·&nbsp; Inspired by Sandeep Jethwani's Subscription Economy Analysis
        </p>
    </div>
    <div style="height:16px;"></div>
    """, unsafe_allow_html=True)

    # ── Session state ─────────────────────────────────────────────────────────
    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []

    # ══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════════════════════
    with st.sidebar:
        st.markdown(f"<div style='font-size:15px;font-weight:700;color:{DARK['text']};margin-bottom:12px;'>➕ Add Subscription</div>", unsafe_allow_html=True)

        search_name = st.text_input("Search App", placeholder="Netflix, Spotify, Swiggy…", label_visibility="collapsed")

        found_data, found_source, manual_price = None, "", None

        if search_name:
            found_data, found_source = resolve_price(search_name)
            if found_data:
                st.markdown(
                    f"""<div style="background:{DARK['card']};border:1px solid #1B5E20;border-left:3px solid #A5D6A7;
                        border-radius:0 8px 8px 0;padding:10px 12px;margin:8px 0;font-size:12px;color:{DARK['text']};">
                        <b style='color:#A5D6A7;'>Found:</b> {found_data['display']}<br>
                        <span style='color:{DARK['muted']};'>{found_data['category']} · {found_source}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )
                manual_price = st.number_input("Monthly Price (INR)", 1, 50000, found_data["price"], 10)
            else:
                st.markdown(
                    f"""<div style="background:{DARK['card']};border-left:3px solid #FFB74D;
                        border-radius:0 8px 8px 0;padding:10px 12px;margin:8px 0;font-size:12px;
                        color:{DARK['muted']};">Not in database — enter price manually</div>""",
                    unsafe_allow_html=True,
                )
                manual_price = st.number_input("Monthly Price (INR)", 1, 50000, 299, 10)

        if st.button("Add to Portfolio"):
            if search_name and manual_price:
                entry = {
                    "display":  found_data["display"]  if found_data else search_name.title(),
                    "category": found_data["category"] if found_data else "Other",
                    "price":    manual_price,
                }
                existing = [s["display"] for s in st.session_state.portfolio]
                if entry["display"] not in existing:
                    st.session_state.portfolio.append(entry)
                    st.rerun()
                else:
                    st.error("Already in portfolio!")
            else:
                st.error("Enter an app name first.")

        st.markdown(f"<hr style='border-color:{DARK['border']};margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:12px;font-weight:600;color:{DARK['muted']};text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;'>Quick Add</div>", unsafe_allow_html=True)

        quick_apps = [
            ("Netflix Standard", "🎬"), ("Amazon Prime", "📦"),
            ("YouTube Premium", "▶️"), ("Spotify Premium", "🎵"),
            ("Disney+ Hotstar", "🏏"), ("Zomato Gold", "🍔"),
            ("Swiggy One", "🛵"),      ("Microsoft 365", "💼"),
        ]
        cols = st.columns(2)
        for i, (app, emoji) in enumerate(quick_apps):
            with cols[i % 2]:
                if st.button(f"{emoji} {app.split()[0]}", key=f"q_{app}"):
                    data, src = resolve_price(app)
                    if data:
                        existing = [s["display"] for s in st.session_state.portfolio]
                        if data["display"] not in existing:
                            st.session_state.portfolio.append({**data})
                            st.rerun()

        st.markdown(f"<hr style='border-color:{DARK['border']};margin:16px 0;'>", unsafe_allow_html=True)

        portfolio = st.session_state.portfolio
        if portfolio:
            st.markdown(f"<div style='font-size:12px;font-weight:600;color:{DARK['muted']};text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px;'>Your Portfolio ({len(portfolio)})</div>", unsafe_allow_html=True)
            total_mo = sum(s["price"] for s in portfolio)
            for i, sub in enumerate(portfolio):
                pct = sub["price"] / total_mo * 100 if total_mo else 0
                c1, c2 = st.columns([4, 1])
                c1.markdown(
                    f"<div style='font-size:12px;'><b style='color:{DARK['text']};'>{sub['display']}</b>"
                    f"<br><span style='color:{DARK['muted']};'>₹{sub['price']:,}/mo · {pct:.0f}%</span></div>",
                    unsafe_allow_html=True,
                )
                if c2.button("✕", key=f"rm_{i}"):
                    st.session_state.portfolio.pop(i)
                    st.rerun()

            st.markdown(
                f"<div style='background:{DARK['card']};border-radius:8px;padding:10px 12px;margin-top:8px;text-align:center;'>"
                f"<span style='color:{DARK['muted']};font-size:12px;'>Total Monthly</span><br>"
                f"<span style='color:{DARK['gold']};font-size:1.4rem;font-weight:700;'>₹{total_mo:,}</span></div>",
                unsafe_allow_html=True,
            )

            if st.button("Clear All", key="clear_all"):
                st.session_state.portfolio = []
                st.rerun()
        else:
            st.markdown(
                f"<div style='color:{DARK['muted']};font-size:12px;text-align:center;padding:12px;'>No subscriptions yet</div>",
                unsafe_allow_html=True,
            )

        st.markdown(f"<hr style='border-color:{DARK['border']};margin:16px 0;'>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:11px;color:{DARK['muted']};'>Benchmarks used:</div>", unsafe_allow_html=True)
        for bm_name, bm in BENCHMARKS.items():
            st.markdown(
                f"<div style='font-size:11px;color:{bm['color']};padding:2px 0;'>{bm['icon']} {bm_name}</div>",
                unsafe_allow_html=True,
            )

    # ══════════════════════════════════════════════════════════════════════════
    # MAIN PANEL
    # ══════════════════════════════════════════════════════════════════════════
    portfolio = st.session_state.portfolio

    if not portfolio:
        st.markdown(f"""
        <div style="text-align:center;padding:100px 20px;color:{DARK['muted']};">
            <div style="font-size:72px;margin-bottom:20px;opacity:.6;">💸</div>
            <h2 style="color:{DARK['text']};font-weight:700;font-size:1.5rem;">Add your first subscription</h2>
            <p style="font-size:14px;max-width:400px;margin:8px auto;">
                Search for apps like Netflix, Spotify, or Swiggy in the sidebar —
                or hit Quick Add to start instantly.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    total_monthly = sum(s["price"] for s in portfolio)

    # ── Totals panel ─────────────────────────────────────────────────────────
    render_totals_panel(portfolio)

    # ── Wealth gap alert ──────────────────────────────────────────────────────
    eq_10y  = sip_fv(total_monthly, 12.0, 120)
    gap_eq  = eq_10y - total_monthly * 120
    daily   = total_monthly / 30
    coffees = int(daily / 60)

    st.markdown(
        f"""<div style="background:linear-gradient(135deg,#1A0A0A 0%,#2A0F0F 100%);
                border:1px solid {DARK['red']};border-left:5px solid {DARK['red']};
                border-radius:12px;padding:20px 24px;margin:4px 0 8px;display:flex;
                align-items:center;gap:24px;flex-wrap:wrap;">
            <div style="font-size:40px;">🔥</div>
            <div>
                <div style="font-size:13px;font-weight:600;color:#EF9A9A;text-transform:uppercase;letter-spacing:.06em;">Wealth Opportunity Cost</div>
                <div style="font-size:1.6rem;font-weight:800;color:#FF5252;margin:4px 0;">
                    {fmt_inr(gap_eq)} missed over 10 years
                </div>
                <div style="font-size:13px;color:{DARK['muted']};">
                    Spending <b style="color:#EF9A9A;">₹{total_monthly:,}/month</b> on subscriptions
                    instead of an Equity SIP costs you <b style="color:#FF5252;">{fmt_inr(gap_eq)}</b> in potential wealth.
                    That's ₹{daily:.0f}/day — or {coffees} cups of chai ☕ every single day!
                </div>
            </div>
        </div>""",
        unsafe_allow_html=True,
    )

    # ══════════════════════════════════════════════════════════════════════════
    # CHARTS — Tabbed layout
    # ══════════════════════════════════════════════════════════════════════════
    section_header("📊 Visual Analytics", "Six chart types — wealth gap, projections, categories, break-even, radar & heatmap")

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Wealth Gap", "Projections", "Category Spend",
        "Break-Even", "Radar View", "Growth Heatmap",
    ])

    with tab1:
        st.plotly_chart(chart_wealth_gap(total_monthly), use_container_width=True)
        info_box(
            "The shaded area between <b>Total Spent</b> and the <b>Equity curve</b> is your "
            f"<b style='color:{DARK['gold']};'>Wealth Gap</b>. Annotations mark 3Y, 5Y, and 10Y milestones.",
            DARK["accent"]
        )

    with tab2:
        st.plotly_chart(chart_bar_comparison(portfolio), use_container_width=True)
        info_box(
            "Each cluster shows what that subscription's monthly cost would grow to over 10 years "
            "under each investment scenario vs. simply spending it.",
            DARK["green"]
        )

    with tab3:
        col_donut, col_waterfall = st.columns(2)
        with col_donut:
            st.plotly_chart(chart_donut_category(portfolio), use_container_width=True)
        with col_waterfall:
            st.plotly_chart(chart_waterfall_total(portfolio), use_container_width=True)
        info_box(
            "Left: Share of your wallet by category. Right: Each subscription's contribution to total monthly burn.",
            DARK["muted"]
        )

    with tab4:
        st.plotly_chart(chart_break_even(portfolio), use_container_width=True)
        info_box(
            "<b>Break-even</b> is the month when your SIP returns first exceed the total amount invested. "
            "For Equity (12%), this typically happens within the first few months due to compounding.",
            DARK["gold"]
        )

    with tab5:
        st.plotly_chart(chart_milestone_radar(total_monthly), use_container_width=True)
        info_box(
            "Spider chart showing portfolio SIP value at 1, 3, 5, and 10 year milestones for all three benchmarks.",
            DARK["accent"]
        )

    with tab6:
        if len(portfolio) > 0:
            st.plotly_chart(chart_yearly_growth_heatmap(portfolio), use_container_width=True)
            info_box(
                "Equity SIP (12% p.a.) growth per subscription at each year milestone. "
                "Darker = lower value, brighter gold = higher compounded wealth.",
                DARK["gold"]
            )

    # ── Projection table ──────────────────────────────────────────────────────
    section_header("📋 Full Projection Table", "All subscriptions × all scenarios × 1Y / 3Y / 5Y / 10Y")

    rows = []
    for sub in portfolio:
        P = sub["price"]
        for bm_name, bm in BENCHMARKS.items():
            rows.append({
                "Subscription":   sub["display"],
                "Category":       sub["category"],
                "Monthly":        f"₹{P:,}",
                "Scenario":       bm_name,
                "1Y Value":       fmt_inr(sip_fv(P, bm["rate"], 12)),
                "3Y Value":       fmt_inr(sip_fv(P, bm["rate"], 36)),
                "5Y Value":       fmt_inr(sip_fv(P, bm["rate"], 60)),
                "10Y Value":      fmt_inr(sip_fv(P, bm["rate"], 120)),
                "10Y Gain":       fmt_inr(sip_fv(P, bm["rate"], 120) - P * 120),
            })

    # Totals row per benchmark
    for bm_name, bm in BENCHMARKS.items():
        rows.append({
            "Subscription":   "TOTAL",
            "Category":       "—",
            "Monthly":        f"₹{total_monthly:,}",
            "Scenario":       bm_name,
            "1Y Value":       fmt_inr(sip_fv(total_monthly, bm["rate"], 12)),
            "3Y Value":       fmt_inr(sip_fv(total_monthly, bm["rate"], 36)),
            "5Y Value":       fmt_inr(sip_fv(total_monthly, bm["rate"], 60)),
            "10Y Value":      fmt_inr(sip_fv(total_monthly, bm["rate"], 120)),
            "10Y Gain":       fmt_inr(sip_fv(total_monthly, bm["rate"], 120) - total_monthly * 120),
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=min(500, 60 + len(df) * 36), hide_index=True)

    # ── Excel export ──────────────────────────────────────────────────────────
    section_header("📥 Export Report")

    c1, c2 = st.columns([1, 2])
    with c1:
        if st.button("Generate Excel Report"):
            with st.spinner("Building workbook…"):
                xls = generate_excel(portfolio)
            st.download_button(
                "⬇️ Download Opportunity_Cost_India.xlsx",
                data=xls,
                file_name="Subscription_Opportunity_Cost_India.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    with c2:
        info_box(
            "Excel includes:<br>"
            "• <b>Summary sheet</b> — all subs × all scenarios × 1/3/5/10Y + Totals row<br>"
            "• <b>Monthly Detail sheet</b> — 120-month compounding breakdown for your full portfolio<br>"
            "• Dark-themed formatting, INR currency, freeze panes",
            DARK["accent"]
        )

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="border-top:1px solid {DARK['border']};margin-top:40px;padding:20px 0;
                text-align:center;color:{DARK['muted']};font-size:11px;line-height:1.8;">
        <b>Formula:</b> FV = P × [((1+r)ⁿ − 1) / r] × (1+r) &nbsp;·&nbsp;
        Monthly compounding (SIP-style) &nbsp;·&nbsp;
        Benchmarks: FD 6% | Debt Fund 8% | Equity/Index 12% p.a.<br>
        Past performance does not guarantee future returns. For educational use only.
        Consult a SEBI-registered investment advisor before making investment decisions.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
