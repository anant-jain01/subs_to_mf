# Project Specification: Subscription Opportunity Cost Calculator (India Edition)

## 1. Overview
**Inspiration:** Based on Sandeep Jethwani’s "Subscription Economy" analysis.
**Goal:** A tool to visualize the "True Cost" of monthly subscriptions by comparing them against potential SIP returns in Indian market instruments (FD, Debt, Equity).

---

## 2. Technical Requirements: The Excel File
Generate a downloadable `.xlsx` file with the following:
- **Columns:** Subscription Name, Monthly Cost (INR), 1Y Growth, 3Y Growth, 5Y Growth, 10Y Growth.
- **SIP Logic:** Use the Future Value of an Annuity Due formula:
  $$FV = P \times \frac{(1 + r)^n - 1}{r} \times (1 + r)$$
  *Where:* - $P$ = Monthly Subscription Cost
  - $r$ = Annual Rate / 12 / 100
  - $n$ = Number of months

---

## 3. Technical Requirements: The Web App (Streamlit)
Develop a Python-based Streamlit app with these features:

### A. Smart Input & Price Retrieval
- **Search Bar:** User types an app name (e.g., "Netflix").
- **Pricing Engine:** 1. Attempt to scrape current India prices using `BeautifulSoup`.
  2. **Fallback Dictionary:** If scraping fails, use this pre-defined list:
     - Netflix (Standard): ₹499
     - Amazon Prime: ₹299
     - YouTube Premium: ₹149
     - Zomato Gold: ₹100
     - Swiggy One: ₹150
     - Spotify Premium: ₹119
     - Disney+ Hotstar: ₹299

### B. Live Dashboard & Scenarios
- **Scenario 1:** FD (Expected 6% p.a.)
- **Scenario 2:** Debt Fund (Expected 8% p.a.)
- **Scenario 3:** Equity/Index Fund (Expected 12% p.a.)
- **Metric:** Display "Wealth Lost" — The difference between total spent vs. Equity returns over 10 years.

### C. Visualizations
- **Line Chart:** Growth curves of the 3 investment types vs. "Linear Expense" (Total spent without interest) over a 120-month timeline.

---

## 4. Market Context (India)
- **Currency:** INR (₹)
- **Frequency:** Monthly Compounding (SIP Style)
- **Return Benchmarks:** 6% (Low Risk), 8% (Mid Risk), 12% (High Risk)

---

## 5. Developer Prompt for Claude
"Claude, please write the complete Python code for the Streamlit web app described above. 
1. Use `pandas` and `numpy` for calculations.
2. Use `plotly` or `streamlit.line_chart` for visuals.
3. Include a function using `xlsxwriter` to allow the user to download the Excel Template directly from the app.
4. Ensure the UI feels premium and reflects Indian financial terminology."

# PROJECT SPECIFICATION: Subscription Opportunity Cost Calculator (India)

## 1. Objective
Build an analysis tool (Excel + Web App) that calculates the "Wealth Opportunity Cost" of monthly subscriptions in the Indian market, comparing them against SIP returns in FD, Debt, and Equity.

## 2. Investment Benchmarks (India)
- FD (Fixed Deposit): 6% Annual Return
- Debt Funds: 8% Annual Return
- Equity (Index/Mutual Funds): 12% Annual Return

## 3. Tool Requirements

### A. Excel File Generation
- **Inputs:** Subscription Name, Monthly Cost (INR).
- **Calculations:** Monthly, Yearly, 3yr, 5yr, and 10yr growth.
- **Formula:** Use Monthly SIP Compounding: FV = P × [((1 + r)^n - 1) / r] × (1 + r)
  (Where P = Monthly cost, r = Annual rate/12, n = number of months)

### B. Python Web App (Streamlit)
- **Feature 1 (Web Scraping):** Allow user to input an app name (e.g., Netflix, Zomato Gold). Scrape or use a lookup dictionary for India-specific pricing.
- **Feature 2 (Calculation):** Show a table comparing growth across the 3 benchmarks.
- **Feature 3 (Insight):** Display the "Best Return" after 3, 5, and 10 years.
- **Feature 4 (Visuals):** Line chart showing the widening gap between "Total Spent" vs "Potential Wealth."
