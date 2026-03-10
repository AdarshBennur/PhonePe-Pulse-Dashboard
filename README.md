# PhonePe Pulse Dashboard

_Tracking digital payment adoption across India's 36 states — 235 billion transactions, ₹345 trillion in value, 7 years of data._

---

## Live Demo & Code

[Live App](https://phonepe-pulse-dashboard.streamlit.app) · [GitHub](https://github.com/AdarshBennur/PhonePe-Pulse-Dashboard)

---

## Product Overview

PhonePe grew from 1.08 billion transactions in 2018 to 99.3 billion in 2024 — a 91.9× increase. But headline numbers don't tell you which states are maturing, which categories are driving value vs. volume, or where the insurance product has room to grow. This dashboard answers those questions interactively, without writing SQL.

**Who would use this in a real company:** Growth PMs benchmarking state-level penetration, business analysts presenting QBR metrics, strategy teams evaluating insurance rollout priorities.

---

## Analytics & Metrics Layer

### Regional Adoption Patterns
**Question:** Which states lead, and where does growth remain untapped?
**What the data shows:** Maharashtra leads all-time with 31.99B transactions, followed by Karnataka (30.97B) and Telangana (26.17B). The choropleth maps reveal a count-vs-value split — states with fewer transactions can rank higher on average transaction value, a signal that a premium user segment exists outside the top metros. District-level data covers 843 districts and shows sub-state pockets that state aggregates mask.
**Decision it drives:** Where to expand merchant acquisition vs. where to increase spend-per-user.

### Transaction Behavior by Category
**Question:** Which of the 5 transaction types drives volume, and which drives revenue?
**What the data shows:** Merchant payments leads by count (130.24B transactions) but Peer-to-peer payments leads by rupee value (₹266.53T — 77% of all transaction value). Recharge & bill payments adds 19.60B transactions at ₹13.34T. Financial Services and Others together total 416M transactions, a clear long-tail.
**Decision it drives:** These two metrics point to different product lines. Reporting a single "transaction health score" conflates them — they need separate tracking.

### Growth Trends (2018–2024)
**Question:** Is platform growth accelerating or decelerating, and is that seasonal or structural?
**What the data shows:** YoY transaction growth rates: 2018→2019 was ~3.8×, 2019→2020 ~2×, 2020→2021 ~2.4×, 2021→2022 ~2×, 2022→2023 ~1.6×, 2023→2024 ~1.5×. The Trends page computes quarter-over-quarter growth rates across transactions, users, and insurance simultaneously — so you can see if a deceleration quarter is platform-wide or category-specific.
**Decision it drives:** Calibrating annual growth targets; distinguishing saturation in high-penetration states from opportunity in low-penetration ones.

### User Registration & Engagement Segmentation
**Question:** Are registered users active, and which states have an engagement gap?
**What the data shows:** 8.86B cumulative registered users generated 402.29B app opens. The dashboard computes opens-per-user at the state level as a stickiness proxy. States are segmented into a 3×3 grid: Low/Medium/High Adoption × Low/Medium/High Engagement. High-registration, low-engagement states are the re-engagement opportunity; low-registration states are the acquisition opportunity.
**Decision it drives:** Allocates re-engagement campaign budget vs. new user acquisition spend by state.

### Insurance Adoption & Penetration
**Question:** Which states are under-penetrated for PhonePe's insurance product given their existing user base?
**What the data shows:** Insurance policies grew 6.4× in 4 years — from 788K in 2020 to 5.07M in 2024. Karnataka leads with 1.96M all-time policies; Maharashtra follows at 1.82M. The penetration metric (insurance_count ÷ registered_users) surfaces states where the user base exists but uptake is low.
**Decision it drives:** Cross-sell targeting — rank states by (user base size × inverse of penetration rate) to prioritize insurance push campaigns.

---

## Key Insights Found

| Insight | Implication | Action |
|---|---|---|
| Merchant payments has 130B transactions; P2P moves ₹266T — 4× more value on fewer transactions | Volume and value metrics point to different products | Track and report them on separate dashboards |
| Transaction growth decelerated from 3.8× to 1.5× YoY between 2018 and 2024 | High-penetration states are maturing | Shift acquisition investment toward states still in early growth phase |
| Insurance grew 6.4× in 4 years but is concentrated in Karnataka and Maharashtra | Product-market fit is proven; distribution is the constraint | Prioritize cross-sell in states with high registered users and low insurance penetration |
| Top 5 states account for a disproportionate share of national transaction volume | Geographic concentration creates platform risk | Deepen incentive programs in mid-tier states to broaden the revenue base |

---

## Tech Stack

| Layer | Tool |
|---|---|
| Dashboard framework | Streamlit |
| Visualizations | Plotly (choropleth, time-series, scatter, sunburst) |
| Data processing | Pandas, NumPy |
| Statistical analysis | SciPy, Statsmodels (OLS trendlines, correlation matrices) |
| Deployment config | GitHub Codespaces (devcontainer) |

---

## Data Source

| | |
|---|---|
| Source | PhonePe Pulse (public dataset) |
| Coverage | 36 states/UTs · 843 districts · Q1 2018 – Q2 2024 |
| Total rows | ~44,600 across 5 CSV tables |
| Tables | aggregated_transactions (5,034) · map_transactions (20,604) · top_performers (18,295) · aggregated_users (1,008) · aggregated_insurance (682) |
| Variables | State, Year, Quarter, Transaction Type, Count, Amount, Registered Users, App Opens, Insurance Count/Amount |

---

## Local Setup

```bash
git clone https://github.com/AdarshBennur/PhonePe-Pulse-Dashboard.git
cd PhonePe-Pulse-Dashboard
pip install -r requirements.txt
streamlit run 🏠_Home.py
```

---

## Author

**Adarsh Bennur** · [adarshbennur.com](https://adarshbennur.com) · [linkedin.com/in/adarshbennur](https://linkedin.com/in/adarshbennur)
