"""
Subscription Opportunity Cost Calculator - India Edition
Mobile-first, deployment-ready Streamlit app.
"""

import base64
import io
import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False



# ─────────────────────────────────────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────────────────────────────────────

PRICING_DATABASE = {
    "netflix standard":     {"price": 499,  "display": "Netflix (Standard)",    "category": "Entertainment", "emoji": "🎬"},
    "netflix basic":        {"price": 199,  "display": "Netflix (Basic)",        "category": "Entertainment", "emoji": "🎬"},
    "netflix mobile":       {"price": 149,  "display": "Netflix (Mobile)",       "category": "Entertainment", "emoji": "🎬"},
    "amazon prime":         {"price": 299,  "display": "Amazon Prime",           "category": "Entertainment", "emoji": "📦"},
    "prime video":          {"price": 299,  "display": "Amazon Prime Video",     "category": "Entertainment", "emoji": "📦"},
    "youtube premium":      {"price": 149,  "display": "YouTube Premium",        "category": "Entertainment", "emoji": "▶️"},
    "youtube":              {"price": 149,  "display": "YouTube Premium",        "category": "Entertainment", "emoji": "▶️"},
    "zomato gold":          {"price": 100,  "display": "Zomato Gold",            "category": "Food & Delivery","emoji": "🍔"},
    "zomato":               {"price": 100,  "display": "Zomato Gold",            "category": "Food & Delivery","emoji": "🍔"},
    "swiggy one":           {"price": 150,  "display": "Swiggy One",             "category": "Food & Delivery","emoji": "🛵"},
    "swiggy":               {"price": 150,  "display": "Swiggy One",             "category": "Food & Delivery","emoji": "🛵"},
    "spotify premium":      {"price": 119,  "display": "Spotify Premium",        "category": "Music",          "emoji": "🎵"},
    "spotify":              {"price": 119,  "display": "Spotify Premium",        "category": "Music",          "emoji": "🎵"},
    "disney+ hotstar":      {"price": 299,  "display": "Disney+ Hotstar",        "category": "Entertainment", "emoji": "🏏"},
    "hotstar":              {"price": 299,  "display": "Disney+ Hotstar",        "category": "Entertainment", "emoji": "🏏"},
    "disney hotstar":       {"price": 299,  "display": "Disney+ Hotstar",        "category": "Entertainment", "emoji": "🏏"},
    "apple music":          {"price": 99,   "display": "Apple Music",            "category": "Music",          "emoji": "🍎"},
    "sony liv":             {"price": 299,  "display": "SonyLIV",                "category": "Entertainment", "emoji": "📺"},
    "sonyliv":              {"price": 299,  "display": "SonyLIV",                "category": "Entertainment", "emoji": "📺"},
    "zee5":                 {"price": 149,  "display": "ZEE5",                   "category": "Entertainment", "emoji": "📺"},
    "jio cinema":           {"price": 29,   "display": "JioCinema Premium",      "category": "Entertainment", "emoji": "🎥"},
    "jiocinema":            {"price": 29,   "display": "JioCinema Premium",      "category": "Entertainment", "emoji": "🎥"},
    "mx player":            {"price": 99,   "display": "MX Player Pro",          "category": "Entertainment", "emoji": "▶️"},
    "mxplayer":             {"price": 99,   "display": "MX Player Pro",          "category": "Entertainment", "emoji": "▶️"},
    "linkedin premium":     {"price": 1300, "display": "LinkedIn Premium",       "category": "Professional",  "emoji": "💼"},
    "linkedin":             {"price": 1300, "display": "LinkedIn Premium",       "category": "Professional",  "emoji": "💼"},
    "adobe creative cloud": {"price": 1675, "display": "Adobe Creative Cloud",   "category": "Productivity",  "emoji": "🎨"},
    "adobe":                {"price": 1675, "display": "Adobe Creative Cloud",   "category": "Productivity",  "emoji": "🎨"},
    "microsoft 365":        {"price": 420,  "display": "Microsoft 365 Personal", "category": "Productivity",  "emoji": "💻"},
    "microsoft":            {"price": 420,  "display": "Microsoft 365 Personal", "category": "Productivity",  "emoji": "💻"},
    "google one":           {"price": 130,  "display": "Google One (100 GB)",    "category": "Storage",        "emoji": "☁️"},
    "dropbox":              {"price": 800,  "display": "Dropbox Plus",           "category": "Storage",        "emoji": "📂"},
    "icloud":               {"price": 75,   "display": "iCloud+ (50 GB)",        "category": "Storage",        "emoji": "☁️"},
    "gympass":              {"price": 599,  "display": "Gympass",                "category": "Health & Fitness","emoji": "💪"},
    "cult fit":             {"price": 999,  "display": "Cult.fit",               "category": "Health & Fitness","emoji": "🏋️"},
    "cultfit":              {"price": 999,  "display": "Cult.fit",               "category": "Health & Fitness","emoji": "🏋️"},
    "duolingo plus":        {"price": 399,  "display": "Duolingo Plus",          "category": "Education",      "emoji": "🦉"},
    "duolingo":             {"price": 399,  "display": "Duolingo Plus",          "category": "Education",      "emoji": "🦉"},
    "coursera plus":        {"price": 3000, "display": "Coursera Plus",          "category": "Education",      "emoji": "🎓"},
    "notion plus":          {"price": 330,  "display": "Notion Plus",            "category": "Productivity",  "emoji": "📝"},
    "notion":               {"price": 330,  "display": "Notion Plus",            "category": "Productivity",  "emoji": "📝"},
    "canva pro":            {"price": 499,  "display": "Canva Pro",              "category": "Productivity",  "emoji": "🎨"},
    "canva":                {"price": 499,  "display": "Canva Pro",              "category": "Productivity",  "emoji": "🎨"},
    "grammarly premium":    {"price": 1000, "display": "Grammarly Premium",      "category": "Productivity",  "emoji": "✍️"},
    "grammarly":            {"price": 1000, "display": "Grammarly Premium",      "category": "Productivity",  "emoji": "✍️"},
}

BENCHMARKS = {
    "FD (6% p.a.)":           {"rate": 6.0,  "color": "#4FC3F7", "fill": "rgba(79,195,247,0.12)",  "icon": "🏦"},
    "Debt Fund (8% p.a.)":    {"rate": 8.0,  "color": "#A5D6A7", "fill": "rgba(165,214,167,0.12)", "icon": "📊"},
    "Equity Fund (12% p.a.)": {"rate": 12.0, "color": "#FFB74D", "fill": "rgba(255,183,77,0.15)",  "icon": "🚀"},
}

CATEGORY_COLORS = {
    "Entertainment":   "#7B61FF",
    "Food & Delivery": "#FF6B6B",
    "Music":           "#4FC3F7",
    "Productivity":    "#81C784",
    "Professional":    "#FFB74D",
    "Storage":         "#F06292",
    "Health & Fitness":"#80CBC4",
    "Education":       "#FFD54F",
    "Finance":         "#90A4AE",
    "Other":           "#B0BEC5",
}

QUICK_APPS = [
    ("Netflix Standard", "🎬", 499),  ("Amazon Prime", "📦", 299),
    ("YouTube Premium", "▶️", 149),   ("Spotify Premium", "🎵", 119),
    ("Disney+ Hotstar", "🏏", 299),   ("Zomato Gold", "🍔", 100),
    ("Swiggy One", "🛵", 150),         ("Microsoft 365", "💻", 420),
    ("Canva Pro", "🎨", 499),          ("Duolingo Plus", "🦉", 399),
]

HORIZON_MONTHS = 120

# ─────────────────────────────────────────────────────────────────────────────
# MATH
# ─────────────────────────────────────────────────────────────────────────────

def sip_fv(P: float, annual_pct: float, months: int) -> float:
    if P == 0 or months == 0:
        return 0.0
    if annual_pct == 0:
        return float(P * months)
    r = annual_pct / 12 / 100
    return float(P * (((1 + r) ** months - 1) / r) * (1 + r))


def growth_series(P: float, annual_pct: float, months: int) -> np.ndarray:
    if P == 0:
        return np.zeros(months)
    n = np.arange(1, months + 1, dtype=float)
    if annual_pct == 0:
        return P * n
    r = annual_pct / 12 / 100
    return P * (((1 + r) ** n - 1) / r) * (1 + r)


def invested_series(P: float, months: int) -> np.ndarray:
    return P * np.arange(1, months + 1, dtype=float)


# ─────────────────────────────────────────────────────────────────────────────
# PRICING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

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
            headers = {"User-Agent": "Mozilla/5.0 (compatible; SIPCalc/1.0)"}
            url = "https://www.google.com/search?q=" + name.replace(" ", "+") + "+monthly+subscription+price+India+INR"
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.ok:
                text = BeautifulSoup(resp.text, "html.parser").get_text()
                prices = re.findall(r"[\u20b9]\s*(\d+(?:,\d+)?)", text)
                if prices:
                    val = int(prices[0].replace(",", ""))
                    if 10 <= val <= 15000:
                        return {"price": val, "display": name.title(), "category": "Other", "emoji": "📱"}, "web"
        except Exception:
            pass
    return None, "not_found"


# ─────────────────────────────────────────────────────────────────────────────
# FORMATTING
# ─────────────────────────────────────────────────────────────────────────────

def fmt(amount: float, short: bool = False) -> str:
    sign = "-" if amount < 0 else ""
    a = abs(amount)
    if short:
        if a >= 1_00_00_000: return f"{sign}\u20b9{a/1_00_00_000:.2f} Cr"
        if a >= 1_00_000:    return f"{sign}\u20b9{a/1_00_000:.1f} L"
        if a >= 1_000:       return f"{sign}\u20b9{a/1_000:.1f}K"
        return f"{sign}\u20b9{a:.0f}"
    if a >= 1_00_00_000: return f"{sign}\u20b9{a/1_00_00_000:.2f} Cr"
    if a >= 1_00_000:    return f"{sign}\u20b9{a/1_00_000:.2f} L"
    return f"{sign}\u20b9{a:,.0f}"


# ─────────────────────────────────────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────────────────────────────────────

_BG   = "#0A0E1A"
_SURF = "#0F1629"
_GRID = "#1A2340"
_FONT = dict(family="Inter, system-ui, sans-serif", color="#E8EAF0")


def _layout(title: str = "", height: int = 380) -> dict:
    return dict(
        paper_bgcolor=_BG, plot_bgcolor=_SURF, font=_FONT,
        title=dict(text=f"<b>{title}</b>",
                   font=dict(size=13, color="#FFFFFF"),
                   x=0.0, y=0.98, xanchor="left", pad=dict(l=4)),
        legend=dict(bgcolor="#0F1629", bordercolor="#1A2340", borderwidth=1,
                    font=dict(size=10), orientation="h",
                    yanchor="bottom", y=-0.30, xanchor="center", x=0.5),
        margin=dict(l=10, r=10, t=46, b=96),
        height=height,
        xaxis=dict(gridcolor=_GRID, zeroline=False, tickfont=dict(size=10), automargin=True),
        yaxis=dict(gridcolor=_GRID, zeroline=False, tickfont=dict(size=10), automargin=True),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#0F1629", bordercolor="#1A2340", font=dict(size=11)),
    )


def chart_wealth_gap(P: float) -> go.Figure:
    months   = np.arange(1, HORIZON_MONTHS + 1)
    invested = invested_series(P, HORIZON_MONTHS)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=invested, name="Total Spent",
        line=dict(color="#546E7A", width=2, dash="dot"),
        fill="tozeroy", fillcolor="rgba(84,110,122,0.07)",
        hovertemplate="Month %{x}<br>Spent: \u20b9%{y:,.0f}<extra></extra>",
    ))
    fills = ["tozeroy", "tonexty", "tonexty"]
    for (bm_name, bm), fill in zip(BENCHMARKS.items(), fills):
        s = growth_series(P, bm["rate"], HORIZON_MONTHS)
        fig.add_trace(go.Scatter(
            x=months, y=s, name=bm_name,
            line=dict(color=bm["color"], width=2.5),
            fill=fill, fillcolor=bm["fill"],
            hovertemplate=f"{bm_name} mo%{{x}}: \u20b9%{{y:,.0f}}<extra></extra>",
        ))
    for mo, label in [(36, "3Y"), (60, "5Y"), (120, "10Y")]:
        eq_val = growth_series(P, 12.0, HORIZON_MONTHS)[mo - 1]
        fig.add_vline(x=mo, line=dict(color="#1E2D50", width=1, dash="dash"))
        fig.add_annotation(
            x=mo, y=eq_val,
            text=f"<b>{label}</b><br>{fmt(eq_val, short=True)}",
            showarrow=False, yshift=14,
            font=dict(size=9, color="#FFB74D"),
            bgcolor="#0F1629", borderpad=3,
        )
    lo = _layout("Wealth Gap — Spend vs SIP Returns (10 Years)", height=420)
    lo["xaxis"]["title"] = "Month"
    lo["yaxis"].update(tickprefix="\u20b9", tickformat=",")
    fig.update_layout(**lo)
    return fig


def chart_bar_comparison(portfolio: list) -> go.Figure:
    labels = [s["display"].replace(" (", "<br>(") for s in portfolio]
    fig = go.Figure()
    for cat, rate, color in [
        ("Total Spent", 0,    "#546E7A"),
        ("FD 6%",       6.0,  "#4FC3F7"),
        ("Debt 8%",     8.0,  "#A5D6A7"),
        ("Equity 12%",  12.0, "#FFB74D"),
    ]:
        vals = [s["price"] * 120 if rate == 0 else sip_fv(s["price"], rate, 120) for s in portfolio]
        fig.add_trace(go.Bar(
            name=cat, x=labels, y=vals,
            marker=dict(color=color, line=dict(width=0)),
            text=[fmt(v, short=True) for v in vals],
            textposition="outside", textfont=dict(size=9, color="#FFFFFF"),
            hovertemplate=f"{cat}: \u20b9%{{y:,.0f}}<extra></extra>",
        ))
    lo = _layout("10-Year Projection Per Subscription", height=420)
    lo["barmode"] = "group"
    lo["yaxis"].update(tickprefix="\u20b9", tickformat=",")
    fig.update_layout(**lo)
    return fig


def chart_donut(portfolio: list) -> go.Figure:
    cat_totals: dict = {}
    for s in portfolio:
        cat_totals[s["category"]] = cat_totals.get(s["category"], 0) + s["price"]
    labels = list(cat_totals.keys())
    values = list(cat_totals.values())
    colors = [CATEGORY_COLORS.get(l, "#B0BEC5") for l in labels]
    total_mo = sum(values)
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.65,
        marker=dict(colors=colors, line=dict(color="#0A0E1A", width=2)),
        textinfo="percent", textfont=dict(size=10),
        hovertemplate="%{label}<br>\u20b9%{value:,.0f}/mo (%{percent})<extra></extra>",
        pull=[0.05 if v == max(values) else 0 for v in values],
    ))
    fig.add_annotation(
        text=f"<b>{fmt(total_mo)}</b><br><span style='font-size:9px'>/ month</span>",
        x=0.5, y=0.5, showarrow=False, font=dict(size=13, color="#FFFFFF"),
    )
    lo = _layout("Spend by Category", height=360)
    lo["legend"].update(orientation="v", yanchor="middle", y=0.5,
                        xanchor="left", x=1.0, bgcolor="rgba(0,0,0,0)")
    lo["margin"] = dict(l=10, r=110, t=46, b=20)
    fig.update_layout(**lo)
    return fig


def chart_waterfall(portfolio: list) -> go.Figure:
    subs   = sorted(portfolio, key=lambda s: s["price"], reverse=True)
    names  = [s["display"].split()[0] for s in subs]
    prices = [s["price"] for s in subs]
    total  = sum(prices)
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * len(subs) + ["total"],
        x=names + ["TOTAL"],
        y=prices + [0],
        connector=dict(line=dict(color="#1A2340", width=1)),
        increasing=dict(marker=dict(color="#4FC3F7")),
        totals=dict(marker=dict(color="#FFB74D")),
        text=[f"\u20b9{p:,}" for p in prices] + [f"\u20b9{total:,}"],
        textposition="outside", textfont=dict(size=9, color="#FFFFFF"),
        hovertemplate="%{x}: \u20b9%{y:,.0f}<extra></extra>",
    ))
    lo = _layout("Monthly Burn Breakdown", height=360)
    lo["yaxis"].update(tickprefix="\u20b9", tickformat=",")
    fig.update_layout(**lo)
    return fig


def chart_break_even(P: float) -> go.Figure:
    months   = np.arange(1, HORIZON_MONTHS + 1)
    invested = invested_series(P, HORIZON_MONTHS)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months, y=invested, name="Total Spent",
        line=dict(color="#546E7A", width=2, dash="dot"),
        hovertemplate="Month %{x}: Spent \u20b9%{y:,.0f}<extra></extra>",
    ))
    for bm_name, bm in BENCHMARKS.items():
        s = growth_series(P, bm["rate"], HORIZON_MONTHS)
        crossover = next(
            (i + 1 for i, (sv, iv) in enumerate(zip(s, invested)) if sv >= iv), None
        )
        fig.add_trace(go.Scatter(
            x=months, y=s, name=bm_name,
            line=dict(color=bm["color"], width=2.5),
            hovertemplate=f"{bm_name} mo%{{x}}: \u20b9%{{y:,.0f}}<extra></extra>",
        ))
        if crossover:
            fig.add_annotation(
                x=crossover, y=float(s[crossover - 1]),
                text=f"Mo.{crossover}", showarrow=True,
                arrowhead=2, arrowcolor=bm["color"], arrowsize=0.8,
                font=dict(size=9, color=bm["color"]),
                bgcolor="#0F1629", borderpad=2, ax=25, ay=-28,
            )
    lo = _layout("Break-Even — When SIP Outpaces Total Spend", height=420)
    lo["yaxis"].update(tickprefix="\u20b9", tickformat=",")
    lo["xaxis"]["title"] = "Month"
    fig.update_layout(**lo)
    return fig


def chart_radar(P: float) -> go.Figure:
    horizons = [12, 36, 60, 120]
    labels   = ["1 Year", "3 Years", "5 Years", "10 Years"]
    fig = go.Figure()
    for bm_name, bm in BENCHMARKS.items():
        vals   = [sip_fv(P, bm["rate"], h) for h in horizons]
        vals_c = vals + [vals[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals_c, theta=labels + [labels[0]],
            name=bm_name.split("(")[0].strip(),
            line=dict(color=bm["color"], width=2),
            fill="toself", fillcolor=bm["fill"],
            hovertemplate="%{theta}: \u20b9%{r:,.0f}<extra></extra>",
        ))
    fig.update_layout(
        polar=dict(
            bgcolor=_SURF,
            radialaxis=dict(visible=True, gridcolor=_GRID,
                            tickfont=dict(size=8, color="#6B7A99"),
                            tickprefix="\u20b9", tickformat=","),
            angularaxis=dict(gridcolor=_GRID, tickfont=dict(size=10)),
        ),
        paper_bgcolor=_BG, font=_FONT,
        title=dict(text="<b>Investment Milestone Radar</b>",
                   font=dict(size=13, color="#FFFFFF"), x=0.0),
        legend=dict(bgcolor="#0F1629", bordercolor="#1A2340", borderwidth=1,
                    font=dict(size=10), orientation="h",
                    yanchor="bottom", y=-0.18, xanchor="center", x=0.5),
        margin=dict(l=20, r=20, t=50, b=70),
        height=400,
    )
    return fig


def chart_heatmap(portfolio: list) -> go.Figure:
    years = [1, 2, 3, 5, 7, 10]
    names = [s["display"] for s in portfolio]
    z     = [[sip_fv(s["price"], 12.0, y * 12) for y in years] for s in portfolio]
    text  = [[fmt(v, short=True) for v in row] for row in z]
    fig = go.Figure(go.Heatmap(
        z=z, x=[f"Yr {y}" for y in years], y=names,
        text=text, texttemplate="%{text}",
        colorscale=[
            [0.0, "#0F1629"], [0.3, "#0F3460"],
            [0.6, "#1565C0"], [1.0, "#FFB74D"],
        ],
        hovertemplate="%{y} — %{x}: \u20b9%{z:,.0f}<extra></extra>",
        showscale=False,
    ))
    lo = _layout("Equity SIP Growth Heatmap (12% p.a.)",
                 height=max(280, 130 + len(portfolio) * 44))
    lo["xaxis"]["side"] = "top"
    lo["margin"] = dict(l=10, r=10, t=80, b=20)
    lo["legend"] = dict(visible=False)
    fig.update_layout(**lo)
    return fig


# ─────────────────────────────────────────────────────────────────────────────
# EXCEL EXPORT
# ─────────────────────────────────────────────────────────────────────────────

def generate_excel(portfolio: list) -> bytes:
    out = io.BytesIO()
    wr  = pd.ExcelWriter(out, engine="xlsxwriter")
    wb  = wr.book

    def F(**kw): return wb.add_format(kw)

    f_title = F(bold=True, font_size=13, font_color="#FFFFFF",   bg_color="#0A0E1A")
    f_head  = F(bold=True, font_color="#FFFFFF",  bg_color="#141C35",
                border=1, border_color="#1E2D50", align="center",
                valign="vcenter", text_wrap=True)
    f_sub   = F(bold=True,   font_color="#E8EAF0", bg_color="#0F1629",
                border=1, border_color="#1E2D50")
    f_cat   = F(italic=True, font_color="#6B7A99", bg_color="#0F1629",
                border=1, border_color="#1E2D50")
    f_inr   = F(num_format="\u20b9#,##0", bg_color="#0F1629",
                font_color="#E8EAF0", border=1, border_color="#1E2D50")
    f_gold  = F(num_format="\u20b9#,##0", bg_color="#0F1629",
                font_color="#FFB74D", bold=True, border=1, border_color="#1E2D50")
    f_green = F(num_format="\u20b9#,##0", bg_color="#0F1629",
                font_color="#A5D6A7", border=1, border_color="#1E2D50")
    f_red   = F(num_format="\u20b9#,##0", bg_color="#0F1629",
                font_color="#EF9A9A", bold=True, border=1, border_color="#1E2D50")
    f_mo    = F(num_format="0", bg_color="#0F1629", font_color="#6B7A99",
                border=1, border_color="#1E2D50", align="center")
    f_tot   = F(bold=True, font_size=11, font_color="#FFB74D", bg_color="#141C35",
                border=2, border_color="#4FC3F7", num_format="\u20b9#,##0")
    f_tlbl  = F(bold=True, font_size=11, font_color="#4FC3F7", bg_color="#141C35",
                border=2, border_color="#4FC3F7")

    ws = wb.add_worksheet("Opportunity Cost Summary")
    ws.set_tab_color("#4FC3F7")
    ws.hide_gridlines(2)
    ws.merge_range("A1:P1", "  Subscription Opportunity Cost — India Edition", f_title)
    ws.set_row(0, 28)

    headers = [
        "Subscription", "Category", "Monthly (INR)",
        "1Y FD 6%", "1Y Debt 8%", "1Y Equity 12%",
        "3Y FD 6%", "3Y Debt 8%", "3Y Equity 12%",
        "5Y FD 6%", "5Y Debt 8%", "5Y Equity 12%",
        "10Y FD 6%", "10Y Debt 8%", "10Y Equity 12%",
        "10Y Wealth Gap",
    ]
    widths = [24, 16, 14] + [14] * 12 + [18]
    ws.set_row(1, 34)
    for c, (h, w) in enumerate(zip(headers, widths)):
        ws.write(1, c, h, f_head)
        ws.set_column(c, c, w)

    for ri, sub in enumerate(portfolio):
        dr, P = ri + 2, sub["price"]
        ws.write(dr, 0, sub["display"],  f_sub)
        ws.write(dr, 1, sub["category"], f_cat)
        ws.write(dr, 2, P,               f_inr)
        col = 3
        for n in [12, 36, 60, 120]:
            for rate, fc in [(6.0, f_green), (8.0, f_inr), (12.0, f_gold)]:
                ws.write(dr, col, sip_fv(P, rate, n), fc)
                col += 1
        ws.write(dr, col, sip_fv(P, 12.0, 120) - P * 120, f_red)

    tr = len(portfolio) + 2
    ws.set_row(tr, 26)
    tm = sum(s["price"] for s in portfolio)
    ws.write(tr, 0, "PORTFOLIO TOTAL",         f_tlbl)
    ws.write(tr, 1, f"{len(portfolio)} items", f_tlbl)
    ws.write(tr, 2, tm,                         f_tot)
    col = 3
    for n in [12, 36, 60, 120]:
        for rate in [6.0, 8.0, 12.0]:
            ws.write(tr, col, sip_fv(tm, rate, n), f_tot)
            col += 1
    ws.write(tr, col, sip_fv(tm, 12.0, 120) - tm * 120, f_tot)
    ws.freeze_panes(2, 3)

    ws2 = wb.add_worksheet("Monthly Growth Detail")
    ws2.set_tab_color("#FFB74D")
    ws2.hide_gridlines(2)
    ws2.merge_range("A1:F1",
                    f"  Portfolio Monthly SIP Growth — \u20b9{tm:,}/month combined",
                    f_title)
    ws2.set_row(0, 28)
    dh = ["Month", "Total Invested", "FD 6%", "Debt 8%", "Equity 12%", "Wealth Gap"]
    dw = [10, 17, 16, 16, 18, 17]
    ws2.set_row(1, 32)
    for c, (h, w) in enumerate(zip(dh, dw)):
        ws2.write(1, c, h, f_head)
        ws2.set_column(c, c, w)
    for mo in range(1, HORIZON_MONTHS + 1):
        r, inv = mo + 1, tm * mo
        eq = sip_fv(tm, 12.0, mo)
        ws2.write(r, 0, mo,                   f_mo)
        ws2.write(r, 1, inv,                  f_inr)
        ws2.write(r, 2, sip_fv(tm, 6.0, mo), f_green)
        ws2.write(r, 3, sip_fv(tm, 8.0, mo), f_inr)
        ws2.write(r, 4, eq,                   f_gold)
        ws2.write(r, 5, eq - inv,             f_red)
    ws2.freeze_panes(2, 1)

    wr.close()
    out.seek(0)
    return out.read()


# ─────────────────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.stApp { background: #0A0E1A !important; }
.block-container { padding: 0 1rem 3rem !important; max-width: 1200px !important; }

section[data-testid="stSidebar"] > div {
    background: #0D1120 !important;
    border-right: 1px solid #1A2340 !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: #141C35 !important;
    color: #E8EAF0 !important;
    border: 1px solid #1E2D50 !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: #4FC3F7 !important;
    box-shadow: 0 0 0 2px rgba(79,195,247,0.15) !important;
}
input::placeholder { color: #4A5568 !important; }

.stButton > button {
    background: #141C35 !important;
    color: #E8EAF0 !important;
    border: 1px solid #1E2D50 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 7px 12px !important;
    transition: all 0.15s ease !important;
    width: 100% !important;
}
.stButton > button:hover {
    border-color: #4FC3F7 !important;
    color: #4FC3F7 !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: #0D1120;
    border-radius: 10px;
    gap: 3px; padding: 4px;
    flex-wrap: wrap;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6B7A99 !important;
    border-radius: 7px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    padding: 6px 10px !important;
}
.stTabs [aria-selected="true"] {
    background: #141C35 !important;
    color: #4FC3F7 !important;
}

.stDataFrame { border-radius: 10px !important; }
hr { border-color: #1A2340 !important; margin: 14px 0 !important; }
.stAlert { border-radius: 8px !important; font-size: 13px !important; }

.stDownloadButton > button {
    background: linear-gradient(135deg, #0F3460, #1565C0) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}
.stDownloadButton > button:hover { opacity: 0.88 !important; }

/* Hide Streamlit branding — keep sidebar toggle visible */
#MainMenu { visibility: hidden !important; }
footer { visibility: hidden !important; }
[data-testid="stToolbar"] { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { visibility: hidden !important; }

@media (max-width: 640px) {
    .block-container { padding: 0 0.4rem 2rem !important; }
    .stTabs [data-baseweb="tab"] { font-size: 10px !important; padding: 5px 7px !important; }
}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def kpi(label, value, sub="", icon="", accent="#FFFFFF", sub_color="#A5D6A7"):
    sub_html = (
        f"<div style='font-size:11px;color:{sub_color};margin-top:3px;font-weight:500;"
        f"white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{sub}</div>"
        if sub else ""
    )
    st.markdown(
        f"<div style='background:linear-gradient(145deg,#141C35,#0F1629);"
        f"border:1px solid #1E2D50;border-radius:12px;padding:14px 10px;text-align:center;'>"
        f"<div style='font-size:18px;margin-bottom:2px;'>{icon}</div>"
        f"<div style='font-size:10px;color:#6B7A99;text-transform:uppercase;"
        f"letter-spacing:.09em;margin-bottom:4px;'>{label}</div>"
        f"<div style='font-size:17px;font-weight:700;color:{accent};"
        f"line-height:1.2;word-break:break-word;'>{value}</div>"
        f"{sub_html}</div>",
        unsafe_allow_html=True,
    )


def infobox(html, color="#4FC3F7"):
    st.markdown(
        f"<div style='background:#0D1120;border-left:3px solid {color};"
        f"border-radius:0 8px 8px 0;padding:10px 14px;"
        f"font-size:12px;color:#B0BEC5;line-height:1.5;margin:4px 0 10px;'>{html}</div>",
        unsafe_allow_html=True,
    )


def section(title, subtitle=""):
    sub = f"<p style='color:#6B7A99;font-size:12px;margin:2px 0 0;'>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"<div style='margin:22px 0 10px;'>"
        f"<h2 style='color:#FFFFFF;font-size:1.05rem;font-weight:700;margin:0;"
        f"letter-spacing:-.01em;'>{title}</h2>{sub}</div>",
        unsafe_allow_html=True,
    )


def totals_strip(portfolio):
    tm    = sum(s["price"] for s in portfolio)
    daily = tm / 30

    # ── Year-horizon selector ────────────────────────────────────────────────
    horizon_labels = {"1 Year": 1, "3 Years": 3, "5 Years": 5, "10 Years": 10}
    sel = st.radio(
        "Projection horizon",
        list(horizon_labels.keys()),
        index=3,
        horizontal=True,
        label_visibility="collapsed",
        key="totals_horizon",
    )
    yrs     = horizon_labels[sel]
    months  = yrs * 12
    yr_label = sel  # e.g. "10 Years"

    spent   = tm * months
    fd_val  = sip_fv(tm, 6.0,  months)
    dbt_val = sip_fv(tm, 8.0,  months)
    eq_val  = sip_fv(tm, 12.0, months)
    gap     = eq_val - spent

    st.markdown(
        f"<div style='background:linear-gradient(135deg,#0F1629,#141C35,#0A1628);"
        f"border:1px solid #1E2D50;border-radius:14px;padding:18px 20px;margin:4px 0 14px;overflow-x:auto;'>"
        f"<div style='font-size:10px;color:#6B7A99;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;'>"
        f"Portfolio Total &nbsp;&middot;&nbsp; {len(portfolio)} subscription{'s' if len(portfolio)!=1 else ''}"
        f"&nbsp;&middot;&nbsp; <span style='color:#4FC3F7;'>{yr_label} projection</span>"
        f"</div>"
        f"<div style='display:flex;flex-wrap:wrap;gap:16px 28px;align-items:flex-end;'>"
        f"<div><div style='font-size:11px;color:#6B7A99;margin-bottom:1px;'>Monthly Burn</div>"
        f"<div style='font-size:clamp(1.5rem,5vw,2.4rem);font-weight:800;color:#FFFFFF;line-height:1;'>{fmt(tm)}</div>"
        f"<div style='font-size:11px;color:#6B7A99;margin-top:2px;'>{fmt(daily,short=True)}/day &nbsp;&middot;&nbsp; {fmt(tm*12,short=True)}/yr</div></div>"
        f"<div style='width:1px;background:#1E2D50;height:50px;flex-shrink:0;'></div>"
        f"<div><div style='font-size:11px;color:#6B7A99;margin-bottom:1px;'>{yr_label} Spent</div>"
        f"<div style='font-size:clamp(1.1rem,3.5vw,1.6rem);font-weight:700;color:#EF9A9A;line-height:1;'>{fmt(spent)}</div>"
        f"<div style='font-size:10px;color:#6B7A99;'>if never invested</div></div>"
        f"<div style='width:1px;background:#1E2D50;height:50px;flex-shrink:0;'></div>"
        f"<div><div style='font-size:11px;color:#4FC3F7;margin-bottom:1px;'>FD @ 6%</div>"
        f"<div style='font-size:clamp(1.1rem,3.5vw,1.6rem);font-weight:700;color:#4FC3F7;line-height:1;'>{fmt(fd_val)}</div>"
        f"<div style='font-size:10px;color:#4FC3F7;'>+{fmt(fd_val-spent,short=True)}</div></div>"
        f"<div style='width:1px;background:#1E2D50;height:50px;flex-shrink:0;'></div>"
        f"<div><div style='font-size:11px;color:#A5D6A7;margin-bottom:1px;'>Debt @ 8%</div>"
        f"<div style='font-size:clamp(1.1rem,3.5vw,1.6rem);font-weight:700;color:#A5D6A7;line-height:1;'>{fmt(dbt_val)}</div>"
        f"<div style='font-size:10px;color:#A5D6A7;'>+{fmt(dbt_val-spent,short=True)}</div></div>"
        f"<div style='width:1px;background:#1E2D50;height:50px;flex-shrink:0;'></div>"
        f"<div><div style='font-size:11px;color:#FFB74D;margin-bottom:1px;'>Equity SIP @ 12%</div>"
        f"<div style='font-size:clamp(1.3rem,4vw,2rem);font-weight:800;color:#FFB74D;line-height:1;'>{fmt(eq_val)}</div>"
        f"<div style='font-size:10px;color:#FFB74D;font-weight:600;'>+{fmt(gap,short=True)} wealth created</div></div>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    cols = st.columns(6)
    with cols[0]: kpi("Subs", str(len(portfolio)), icon="📱", accent="#4FC3F7")
    with cols[1]: kpi("Daily", fmt(daily, short=True), icon="📅", accent="#B0BEC5", sub_color="#6B7A99")
    with cols[2]: kpi("Annual", fmt(tm*12, short=True), icon="🔥", accent="#EF9A9A", sub_color="#EF9A9A")
    with cols[3]:
        roi_fd = (fd_val / spent - 1) * 100 if spent else 0
        kpi("FD ROI", f"{roi_fd:.1f}%", f"+{fmt(fd_val-spent,short=True)}", "🏦", "#4FC3F7")
    with cols[4]:
        roi_eq = (eq_val / spent - 1) * 100 if spent else 0
        kpi("Equity ROI", f"{roi_eq:.1f}%", f"+{fmt(gap,short=True)}", "🚀", "#FFB74D")
    with cols[5]:
        biggest = max(portfolio, key=lambda s: s["price"])
        kpi("Top Spend", fmt(biggest["price"], short=True),
            biggest["display"].split()[0], "👑", "#F06292", "#F06292")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Subscription Opportunity Cost — India",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "About": (
                "**Subscription Opportunity Cost Calculator — India Edition**\n\n"
                "Visualize the true wealth cost of monthly subscriptions "
                "vs SIP returns in FD, Debt & Equity.\n\n"
            )
        },
    )

    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # ── Header (logo + title + contact) via components.html to bypass sanitiser ─
    import streamlit.components.v1 as _components
    _logo_b64 = ""
    _logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png")
    if os.path.exists(_logo_path):
        with open(_logo_path, "rb") as _f:
            _logo_b64 = base64.b64encode(_f.read()).decode()
    _logo_tag = (
        f"<img src='data:image/png;base64,{_logo_b64}' "
        f"style='height:56px;width:auto;object-fit:contain;display:block;flex-shrink:0;'>"
        if _logo_b64 else ""
    )
    _components.html(
        f"""
        <style>
          .qbtn {{
            display:inline-block;padding:7px 16px;background:#4FC3F7;color:#0A0E1A;
            font-weight:700;font-size:11px;border-radius:20px;text-decoration:none;
            letter-spacing:.04em;white-space:nowrap;border:none;cursor:pointer;
            transition:background .2s;
          }}
          .qbtn:hover {{ background:#81D4FA; }}
        </style>
        <div style="margin:0;padding:0;font-family:'Segoe UI',Arial,sans-serif;background:#0A0E1A;">

          <!-- contact bar -->
          <div style="background:#060A14;border-bottom:1px solid #243050;
                      padding:6px 20px;font-size:10.5px;color:#90A4AE;
                      display:flex;flex-wrap:wrap;gap:4px 18px;align-items:center;">
            <span>📍 B1/H3 Mohan Co-op Industrial Area, Mathura Road, New Delhi – 110044</span>
            <span style="color:#4FC3F7;">|</span>
            <span>📞 <a href="tel:+919315569603" style="color:#90A4AE;text-decoration:none;">+91 93155 69603</a></span>
            <span style="color:#4FC3F7;">|</span>
            <span>📧 <a href="mailto:support@3kip.in" style="color:#90A4AE;text-decoration:none;">support@3kip.in</a></span>
            <span style="color:#4FC3F7;">|</span>
            <span>🌐 <a href="https://www.3kip.in" target="_blank" style="color:#4FC3F7;text-decoration:none;">www.3kip.in</a></span>
          </div>

          <!-- hero row -->
          <div style="display:flex;align-items:center;gap:16px;padding:12px 20px 11px;
                      background:linear-gradient(135deg,#0F1629 0%,#0A0E1A 100%);
                      border-bottom:1px solid #1A2340;flex-wrap:wrap;">

            <!-- logo on white pill so it stands out -->
            {f'''<div style="background:#FFFFFF;border-radius:10px;padding:6px 10px;
                            display:flex;align-items:center;flex-shrink:0;">
                   {_logo_tag}
                 </div>''' if _logo_b64 else ''}

            <!-- title + subtitle -->
            <div style="flex:1;min-width:200px;">
              <div style="color:#FFFFFF;font-size:clamp(1.05rem,3vw,1.5rem);
                          font-weight:800;letter-spacing:-.02em;line-height:1.2;">
                📊 Subscription Opportunity Cost
              </div>
              <div style="color:#6B7A99;margin:4px 0 0;font-size:11px;
                          display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                <span>India Edition &middot; What your subscriptions could build as SIPs</span>
                <span style="background:#141C35;border:1px solid #1E2D50;border-radius:20px;
                             padding:3px 10px;font-size:10px;color:#4FC3F7;font-weight:600;
                             letter-spacing:.06em;white-space:nowrap;">
                  FD 6% &middot; Debt 8% &middot; Equity 12%
                </span>
              </div>
            </div>

            <!-- Contact Us button -->
            <a class="qbtn" href="javascript:void(0)"
               onclick="window.parent.document.getElementById('for-queries').scrollIntoView({{behavior:'smooth'}});">
              📬 Contact Us
            </a>

          </div>
        </div>
        """,
        height=125,
        scrolling=False,
    )

    if "portfolio" not in st.session_state:
        st.session_state.portfolio = []

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(
            "<div style='font-size:14px;font-weight:700;color:#E8EAF0;"
            "padding:4px 0 10px;border-bottom:1px solid #1A2340;margin-bottom:10px;'>"
            "➕ Add Subscription</div>",
            unsafe_allow_html=True,
        )

        search_name = st.text_input(
            "App name",
            placeholder="e.g. Netflix, Spotify, Swiggy…",
            label_visibility="collapsed",
            key="search_input",
        )

        found_data, found_source, manual_price = None, "", None

        if search_name.strip():
            found_data, found_source = resolve_price(search_name.strip())
            if found_data:
                st.markdown(
                    f"<div style='background:#0A1A10;border-left:3px solid #A5D6A7;"
                    f"border-radius:0 8px 8px 0;padding:8px 10px;margin:6px 0;"
                    f"font-size:11px;color:#E8EAF0;'>"
                    f"<b style='color:#A5D6A7;'>Found:</b> {found_data['display']}<br>"
                    f"<span style='color:#6B7A99;'>{found_data['category']} &middot; {found_source}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                manual_price = st.number_input(
                    "Monthly price (INR)", min_value=1, max_value=50000,
                    value=found_data["price"], step=10, key="price_adj",
                )
            else:
                st.markdown(
                    "<div style='background:#1A1000;border-left:3px solid #FFB74D;"
                    "border-radius:0 8px 8px 0;padding:8px 10px;margin:6px 0;"
                    "font-size:11px;color:#B0BEC5;'>Not found — enter price manually</div>",
                    unsafe_allow_html=True,
                )
                manual_price = st.number_input(
                    "Monthly price (INR)", min_value=1, max_value=50000,
                    value=299, step=10, key="price_manual",
                )

        if st.button("Add to Portfolio", key="add_btn"):
            name_clean = search_name.strip()
            if name_clean and manual_price and int(manual_price) > 0:
                entry = {
                    "display":  found_data["display"]       if found_data else name_clean.title(),
                    "category": found_data["category"]      if found_data else "Other",
                    "emoji":    found_data.get("emoji","📱") if found_data else "📱",
                    "price":    int(manual_price),
                }
                existing = [s["display"] for s in st.session_state.portfolio]
                if entry["display"] not in existing:
                    st.session_state.portfolio.append(entry)
                    st.rerun()
                else:
                    st.warning("Already in portfolio.")
            else:
                st.error("Enter an app name and price.")

        st.markdown(
            "<div style='font-size:10px;font-weight:600;color:#6B7A99;text-transform:uppercase;"
            "letter-spacing:.08em;margin:12px 0 7px;border-top:1px solid #1A2340;"
            "padding-top:12px;'>Quick Add</div>",
            unsafe_allow_html=True,
        )

        qcols = st.columns(2)
        for i, (app, emoji, _price) in enumerate(QUICK_APPS):
            with qcols[i % 2]:
                if st.button(f"{emoji} {app.split()[0]}", key=f"qa_{app}"):
                    data, _src = resolve_price(app)
                    if data:
                        existing = [s["display"] for s in st.session_state.portfolio]
                        if data["display"] not in existing:
                            st.session_state.portfolio.append({**data})
                            st.rerun()

        st.markdown(
            f"<div style='font-size:10px;font-weight:600;color:#6B7A99;text-transform:uppercase;"
            f"letter-spacing:.08em;margin:12px 0 7px;border-top:1px solid #1A2340;"
            f"padding-top:12px;'>Your Portfolio ({len(st.session_state.portfolio)})</div>",
            unsafe_allow_html=True,
        )

        portfolio_sb = st.session_state.portfolio
        if portfolio_sb:
            total_mo_sb = sum(s["price"] for s in portfolio_sb)
            for i, sub in enumerate(portfolio_sb):
                pct = sub["price"] / total_mo_sb * 100
                c1, c2 = st.columns([5, 1])
                c1.markdown(
                    f"<div style='font-size:11px;padding:3px 0;'>"
                    f"<span style='color:#E8EAF0;font-weight:600;'>"
                    f"{sub.get('emoji','📱')} {sub['display']}</span><br>"
                    f"<span style='color:#6B7A99;'>{fmt(sub['price'])}/mo &nbsp;&middot;&nbsp; {pct:.0f}%</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                if c2.button("✕", key=f"rm_{i}", help="Remove"):
                    st.session_state.portfolio.pop(i)
                    st.rerun()

            st.markdown(
                f"<div style='background:#141C35;border-radius:8px;padding:10px;"
                f"text-align:center;margin-top:8px;'>"
                f"<span style='color:#6B7A99;font-size:10px;'>Total Monthly</span><br>"
                f"<span style='color:#FFB74D;font-size:1.3rem;font-weight:800;'>{fmt(total_mo_sb)}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            if st.button("Clear All", key="clear_all"):
                st.session_state.portfolio = []
                st.rerun()
        else:
            st.markdown(
                "<div style='color:#4A5568;font-size:11px;text-align:center;padding:12px 6px;'>"
                "No subscriptions yet.<br>Use Quick Add above!</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<div style='font-size:10px;font-weight:600;color:#6B7A99;text-transform:uppercase;"
            "letter-spacing:.08em;margin:12px 0 6px;border-top:1px solid #1A2340;"
            "padding-top:12px;'>Benchmarks</div>",
            unsafe_allow_html=True,
        )
        for bm_name, bm in BENCHMARKS.items():
            st.markdown(
                f"<div style='font-size:11px;color:{bm['color']};padding:2px 0;'>"
                f"{bm['icon']} {bm_name}</div>",
                unsafe_allow_html=True,
            )
        st.markdown(
            "<div style='font-size:9px;color:#4A5568;margin-top:8px;line-height:1.5;'>"
            "FV = P x [((1+r)^n - 1)/r] x (1+r)<br>"
            "Monthly compounding. Educational use only.</div>",
            unsafe_allow_html=True,
        )

    # ── MAIN CONTENT ────────────────────────────────────────────────────────── 
    portfolio = st.session_state.portfolio

    if not portfolio:
        st.markdown(
            "<div style='text-align:center;padding:36px 16px 18px;'>"
            "<div style='font-size:52px;margin-bottom:10px;'>💸</div>"
            "<h2 style='color:#FFFFFF;font-weight:700;font-size:1.2rem;margin:0 0 6px;'>"
            "Find out what your subscriptions truly cost</h2>"

            "<p style='color:#6B7A99;font-size:13px;max-width:400px;margin:0 auto;'>"
            "Search for an app in the sidebar or tap any card below to start.</p></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div style='font-size:11px;font-weight:600;color:#6B7A99;text-transform:uppercase;"
            "letter-spacing:.08em;text-align:center;margin-bottom:10px;'>Popular in India</div>",
            unsafe_allow_html=True,
        )
        gc = st.columns(2)
        for i, (app, emoji, price) in enumerate(QUICK_APPS):
            with gc[i % 2]:
                if st.button(f"{emoji}  {app}  —  \u20b9{price}/mo", key=f"start_{app}", use_container_width=True):
                    data, _src = resolve_price(app)
                    if data:
                        existing = [s["display"] for s in st.session_state.portfolio]
                        if data["display"] not in existing:
                            st.session_state.portfolio.append({**data})
                            st.rerun()
        return

    total_monthly = sum(s["price"] for s in portfolio)

    totals_strip(portfolio)

    eq_10y  = sip_fv(total_monthly, 12.0, 120)
    gap     = eq_10y - total_monthly * 120
    coffees = max(1, int(total_monthly / 30 / 25))

    st.markdown(
        f"<div style='background:linear-gradient(135deg,#1A0808,#240E0E);"
        f"border:1px solid #5C1A1A;border-left:4px solid #EF5350;"
        f"border-radius:12px;padding:14px 18px;margin:4px 0 8px;"
        f"display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap;'>"
        f"<div style='font-size:28px;flex-shrink:0;'>🔥</div>"
        f"<div style='flex:1;min-width:180px;'>"
        f"<div style='font-size:10px;font-weight:700;color:#EF9A9A;"
        f"text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px;'>Wealth Opportunity Cost</div>"
        f"<div style='font-size:clamp(1rem,3.5vw,1.4rem);font-weight:800;color:#FF5252;margin-bottom:4px;'>"
        f"{fmt(gap)} of profits missed over 10 years</div>"
        f"<div style='font-size:12px;color:#B0BEC5;line-height:1.5;'>"
        f"Spending <b style='color:#EF9A9A;'>{fmt(total_monthly)}/month</b> on subscriptions "
        f"instead of an Equity SIP costs you <b style='color:#FF5252;'>{fmt(gap)}</b> "
        f"</div></div></div>",
        unsafe_allow_html=True,
    )

    section("📊 Analytics", "Tap a tab to explore different views")

    cfg = {"displayModeBar": False, "responsive": True}

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📈 Wealth Gap", "📊 10Y Projection",
        "🍩 Spend Mix",  "⚖️ Break-Even",
        "🕸️ Radar",      "🌡️ Heatmap",
    ])

    with tab1:
        st.plotly_chart(chart_wealth_gap(total_monthly), use_container_width=True, config=cfg)
        infobox("Shaded area between <b>Total Spent</b> and <b>Equity (12%)</b> is your Wealth Gap. Markers show 3Y, 5Y, 10Y values.", "#4FC3F7")

    with tab2:
        st.plotly_chart(chart_bar_comparison(portfolio), use_container_width=True, config=cfg)
        infobox("Each group shows what a subscription's monthly cost becomes after <b>10 years</b> under each investment type vs simply spending it.", "#A5D6A7")

    with tab3:
        cl, cr = st.columns(2)
        with cl:
            st.plotly_chart(chart_donut(portfolio), use_container_width=True, config=cfg)
        with cr:
            st.plotly_chart(chart_waterfall(portfolio), use_container_width=True, config=cfg)
        infobox("Left: wallet share by category. Right: each subscription's share of your monthly burn.", "#6B7A99")

    with tab4:
        st.plotly_chart(chart_break_even(total_monthly), use_container_width=True, config=cfg)
        infobox("<b>Break-even</b> = the month when SIP balance first exceeds total money invested. Equity 12% crosses earliest.", "#FFB74D")

    with tab5:
        st.plotly_chart(chart_radar(total_monthly), use_container_width=True, config=cfg)
        infobox("Spider chart of portfolio SIP value at 1, 3, 5, and 10-year milestones across all three benchmarks.", "#4FC3F7")

    with tab6:
        st.plotly_chart(chart_heatmap(portfolio), use_container_width=True, config=cfg)
        infobox("Equity SIP growth (12% p.a.) per subscription across year milestones. <b>Brighter gold = higher value.</b>", "#FFB74D")

    section("📋 Full Projection Table")

    rows = []
    for sub in portfolio:
        P = sub["price"]
        for bm_name, bm in BENCHMARKS.items():
            rows.append({
                "Subscription": f"{sub.get('emoji','📱')} {sub['display']}",
                "Category":     sub["category"],
                "Monthly":      fmt(P),
                "Scenario":     bm_name,
                "1Y":           fmt(sip_fv(P, bm["rate"], 12),  short=True),
                "3Y":           fmt(sip_fv(P, bm["rate"], 36),  short=True),
                "5Y":           fmt(sip_fv(P, bm["rate"], 60),  short=True),
                "10Y":          fmt(sip_fv(P, bm["rate"], 120), short=True),
                "10Y Gain":     fmt(sip_fv(P, bm["rate"], 120) - P * 120, short=True),
            })
    for bm_name, bm in BENCHMARKS.items():
        rows.append({
            "Subscription": "🏆 PORTFOLIO TOTAL",
            "Category":     "All",
            "Monthly":      fmt(total_monthly),
            "Scenario":     bm_name,
            "1Y":           fmt(sip_fv(total_monthly, bm["rate"], 12),  short=True),
            "3Y":           fmt(sip_fv(total_monthly, bm["rate"], 36),  short=True),
            "5Y":           fmt(sip_fv(total_monthly, bm["rate"], 60),  short=True),
            "10Y":          fmt(sip_fv(total_monthly, bm["rate"], 120), short=True),
            "10Y Gain":     fmt(sip_fv(total_monthly, bm["rate"], 120) - total_monthly * 120, short=True),
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True,
                 height=min(520, 60 + len(rows) * 36), hide_index=True)
    infobox("Last 3 rows = <b>Portfolio Total</b> — combined monthly spend invested as one SIP.", "#FFB74D")

    section("📥 Download Report")
    c1, c2 = st.columns([1, 2])
    with c1:
        excel_bytes = generate_excel(portfolio)
        st.download_button(
            label="⬇️  Download Excel Report",
            data=excel_bytes,
            file_name="Subscription_Opportunity_Cost_India.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    with c2:
        infobox(
            "Includes:<br>"
            "• <b>Summary sheet</b> — all subs x FD/Debt/Equity x 1/3/5/10Y + Portfolio Total<br>"
            "• <b>Monthly Detail</b> — 120-month compounding for your full portfolio<br>"
            "• Dark-themed formatting, INR currency, freeze panes",
            "#4FC3F7",
        )

    # Disclaimer + Footer
    st.markdown(
        "<div style='margin-top:48px;border-top:1px solid #1A2340;padding-top:24px;'></div>",
        unsafe_allow_html=True,
    )

    disclaimer_points = [
        ("Not Investment Advice",
         "This tool is built purely for financial education and awareness. "
         "Nothing here constitutes investment advice, a solicitation to buy or sell "
         "any financial product, or a recommendation of any specific mutual fund, FD, or investment scheme."),
        ("Assumed Returns Are Illustrative",
         "The rates used — 6% (FD), 8% (Debt Fund), 12% (Equity/Index Fund) — are long-term historical "
         "approximations for the Indian market. Actual returns vary based on market conditions, fund selection, "
         "interest rate cycles, inflation, and timing. Equity returns can be negative in any given year."),
        ("Past Performance Is Not a Guarantee",
         "Historical Nifty 50 CAGR of ~12-13% over 20 years does not guarantee future performance. "
         "Debt fund and FD rates fluctuate with RBI monetary policy and broader economic conditions."),
        ("Taxes and Costs Not Modelled",
         "This calculator does not account for LTCG/STCG tax, exit loads, fund expense ratios, "
         "TDS on FD interest, or inflation-adjusted real returns. "
         "Actual post-tax, post-cost returns will be lower than the figures shown."),
        ("Consult a SEBI-Registered Adviser",
         "Before making any investment decision, please consult a SEBI-registered Investment Adviser (RIA) "
         "or a qualified financial planner who can evaluate your personal risk profile, tax bracket, "
         "time horizon, and financial goals."),
    ]

    points_html = "".join(
        f"<div style='margin-bottom:12px;'>"
        f"<span style='color:#90A4AE;font-weight:600;'>{title}. </span>"
        f"<span>{body}</span></div>"
        for title, body in disclaimer_points
    )

    st.markdown(
        f"<div style='background:#0D1120;border:1px solid #1A2340;border-left:3px solid #546E7A;"
        f"border-radius:0 10px 10px 0;padding:18px 22px;max-width:900px;"
        f"margin:0 auto 18px;font-size:12px;color:#607D8B;line-height:1.75;'>"
        f"<div style='font-size:11px;font-weight:700;color:#78909C;text-transform:uppercase;"
        f"letter-spacing:.09em;margin-bottom:12px;'>Important Disclaimer</div>"
        f"{points_html}</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div id='for-queries' style='background:#0D1120;border:1px solid #1A2340;border-left:4px solid #4FC3F7;"
        "border-radius:0 10px 10px 0;padding:18px 22px;max-width:900px;margin:16px auto 8px;'>"
        "<div style='font-size:12px;font-weight:700;color:#4FC3F7;text-transform:uppercase;"
        "letter-spacing:.09em;margin-bottom:10px;'>📬 For Queries</div>"
        "<div style='font-size:12px;color:#90A4AE;line-height:2;'>"
        "<span>📍 B1/H3 Mohan Co-operative Industrial Area, Block B, Mathura Road, New Delhi – 110044, India</span><br>"
        "<span>📞 <a href='tel:+919315569603' style='color:#90A4AE;text-decoration:none;'>+91 93155 69603</a></span>"
        "&nbsp;&nbsp;|&nbsp;&nbsp;"
        "<span>📧 <a href='mailto:support@3kip.in' style='color:#4FC3F7;text-decoration:none;'>support@3kip.in</a></span>"
        "&nbsp;&nbsp;|&nbsp;&nbsp;"
        "<span>🌐 <a href='https://www.3kip.in' target='_blank' style='color:#4FC3F7;text-decoration:none;'>www.3kip.in</a></span>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='background:#060A14;border:1px solid #1A2340;border-radius:10px;"
        "padding:14px 22px;max-width:900px;margin:8px auto 18px;"
        "text-align:center;font-size:11px;color:#546E7A;line-height:2;'>"
        " &nbsp;&middot;&nbsp; Prices from public databases and may not reflect current rates</span>"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
