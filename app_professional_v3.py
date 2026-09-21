import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(
    page_title="Valuation Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Professional styling ----------
st.markdown("""
<style>
:root {
    --navy: #0b2450;
    --blue: #1677ff;
    --light: #f4f7fb;
    --border: #dfe6f0;
    --text: #16213a;
    --muted: #6b7280;
}
.stApp {
    background: linear-gradient(180deg, #eef4fb 0%, #f8fafc 42%, #f4f7fb 100%);
    color: var(--text);
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
[data-testid="stSidebar"] {
    background: #f8fbff;
    border-right: 1px solid #d9e3f0;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
}
.hero {
    background: linear-gradient(120deg, #08224b 0%, #123f86 55%, #1e6fe8 100%);
    color: white;
    border-radius: 18px;
    padding: 28px 32px;
    margin-bottom: 18px;
    box-shadow: 0 12px 30px rgba(10, 43, 90, .18);
}
.hero h1 {
    margin: 0;
    font-size: 2.35rem;
    letter-spacing: -.04em;
}
.hero p {
    margin: 7px 0 0;
    opacity: .88;
    font-size: 1rem;
}
.eyebrow {
    font-size: .78rem;
    font-weight: 800;
    letter-spacing: .16em;
    text-transform: uppercase;
    opacity: .78;
}
.metric-card {
    background: rgba(255,255,255,.96);
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 17px 18px;
    min-height: 116px;
    box-shadow: 0 5px 18px rgba(21, 44, 78, .07);
}
.metric-title {font-size:.86rem;color:#53617a;font-weight:700;}
.metric-value {font-size:1.72rem;font-weight:850;color:#0b2450;margin-top:5px;}
.metric-sub {font-size:.75rem;color:#7a8496;margin-top:3px;}
.section-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 16px rgba(20,45,80,.05);
}
.section-title {font-size:1.15rem;font-weight:800;color:#102a55;}
.section-sub {font-size:.82rem;color:#758096;}
.info-box {
    background:#eef6ff;
    border:1px solid #cfe3ff;
    border-radius:12px;
    padding:12px 14px;
    color:#29456e;
    font-size:.82rem;
}
.stButton > button {
    border-radius: 10px;
    font-weight: 700;
}
div[data-testid="stDataFrame"] {
    border-radius: 12px;
    overflow: hidden;
}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ---------- Data presets ----------
PRESETS = {
    "TCS (Example)": dict(
        shares=361.81, cash=50079.0, debt=0.0, fcf=48424.0,
        ebitda=76800.0, assets=182372.0, liabilities=75800.0,
        market_price=2200.80
    ),
    "Custom Company": dict(
        shares=100.0, cash=1000.0, debt=500.0, fcf=900.0,
        ebitda=1500.0, assets=12000.0, liabilities=7000.0,
        market_price=0.0
    ),
}

# ---------- Sidebar ----------
st.sidebar.markdown("## 🏢 Company Inputs")
st.sidebar.caption("Enter verified company financial information.")

company = st.sidebar.selectbox("Company", list(PRESETS.keys()))
p = PRESETS[company]

shares = st.sidebar.number_input("Shares outstanding (crore)", value=p["shares"], min_value=0.01)
cash = st.sidebar.number_input("Cash + investments (₹ crore)", value=p["cash"], min_value=0.0)
debt = st.sidebar.number_input("Interest-bearing debt (₹ crore)", value=p["debt"], min_value=0.0)
base_fcf = st.sidebar.number_input("Base-year FCF (₹ crore)", value=p["fcf"], min_value=0.0)
market_price = st.sidebar.number_input("Market price (₹/share)", value=p["market_price"], min_value=0.0)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Quick Links")
st.sidebar.markdown("- TCS Investor Relations")
st.sidebar.markdown("- Annual Report")
st.sidebar.markdown("- NSE / BSE filing")

st.sidebar.info("Educational tool only. Verify all inputs from primary filings.")

# ---------- Header ----------
st.markdown("""
<div class="hero">
  <div class="eyebrow">Turn data into value</div>
  <h1>Business Valuation Calculator</h1>
  <p>DCF • Comparable Companies • Precedent Transactions • Asset-Based Valuation</p>
</div>
""", unsafe_allow_html=True)

# ---------- DCF calculation ----------
wacc = 0.1002
terminal_growth = 0.035
growth = [0.05, 0.07, 0.06, 0.05, 0.04]

fcfs, pv_fcfs = [], []
prev = base_fcf
for i, g in enumerate(growth, 1):
    f = prev * (1 + g)
    fcfs.append(f)
    pv_fcfs.append(f / ((1 + wacc) ** i))
    prev = f

terminal_value = fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
pv_terminal = terminal_value / ((1 + wacc) ** 5)
enterprise_dcf = sum(pv_fcfs) + pv_terminal
equity_dcf = enterprise_dcf + cash - debt
dcf_per_share = equity_dcf / shares

# ---------- Comparable companies ----------
peer_data = pd.DataFrame({
    "Peer": ["Infosys", "HCLTech", "Wipro", "Tech Mahindra"],
    "EV/EBITDA (x)": [9.7, 11.7, 7.6, 10.0]
})
median_comp = peer_data["EV/EBITDA (x)"].median()
comp_ev = p["ebitda"] * median_comp
comp_equity = comp_ev + cash - debt
comp_per_share = comp_equity / shares

# ---------- Transactions ----------
tx_data = pd.DataFrame({
    "Transaction": ["Transaction A", "Transaction B", "Transaction C", "Transaction D"],
    "EV/EBITDA (x)": [8.8, 10.4, 9.5, 11.0]
})
median_tx = tx_data["EV/EBITDA (x)"].median()
tx_ev = p["ebitda"] * median_tx
tx_equity = tx_ev + cash - debt
tx_per_share = tx_equity / shares

# ---------- Asset based ----------
assets = p["assets"]
liabilities = p["liabilities"]
net_assets = assets - liabilities
asset_per_share = net_assets / shares

# ---------- Top metrics ----------
cols = st.columns(4)
metrics = [
    ("DCF Value / Share", dcf_per_share, "Based on discounted cash flow"),
    ("Comparable Value / Share", comp_per_share, "Based on peer multiples"),
    ("Transaction Value / Share", tx_per_share, "Based on M&A multiples"),
    ("Asset-Based Value / Share", asset_per_share, "Based on net assets"),
]
for col, (title, value, sub) in zip(cols, metrics):
    col.markdown(
        f"""<div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">₹{value:,.0f}</div>
        <div class="metric-sub">{sub}</div>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------- Tabs ----------
tabs = st.tabs(["📊 DCF", "🏢 Comparable Companies", "🤝 Precedent Transactions", "🏦 Asset-Based", "📋 Summary"])

with tabs[0]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">1. Discounted Cash Flow (DCF) Valuation</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">FCFF/FCF-based simplified DCF. Adjust the assumptions in the controls below.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    base_fcf_input = c1.number_input("Base-year FCF (₹ crore)", value=float(base_fcf))
    wacc_input = c2.number_input("WACC (%)", value=10.02, min_value=0.1, max_value=50.0) / 100
    tg_input = c3.number_input("Terminal growth (%)", value=3.50, min_value=0.0, max_value=9.9) / 100

    gcols = st.columns(5)
    g_input = [
        gcols[i].number_input(f"Year {i+1} growth (%)", value=float(growth[i]*100), key=f"growth_{i}")/100
        for i in range(5)
    ]

    fcfs2, pvs2 = [], []
    prev2 = base_fcf_input
    for i, g in enumerate(g_input, 1):
        f = prev2 * (1 + g)
        fcfs2.append(f)
        pvs2.append(f / ((1 + wacc_input) ** i))
        prev2 = f

    tv2 = fcfs2[-1] * (1 + tg_input) / (wacc_input - tg_input) if wacc_input > tg_input else np.nan
    pvtv2 = tv2 / ((1 + wacc_input) ** 5)
    ev2 = sum(pvs2) + pvtv2
    eq2 = ev2 + cash - debt
    dcf2 = eq2 / shares

    left, mid, right = st.columns([1.2, 1.2, 1])
    with left:
        d = pd.DataFrame({
            "Year": [1,2,3,4,5],
            "Growth %": [x*100 for x in g_input],
            "FCF (₹ cr)": fcfs2,
            "PV (₹ cr)": pvs2,
        })
        st.dataframe(d.style.format({"Growth %":"{:.1f}", "FCF (₹ cr)":"{:,.0f}", "PV (₹ cr)":"{:,.0f}"}), use_container_width=True, hide_index=True)
    with mid:
        fig = go.Figure(go.Bar(x=["Y1","Y2","Y3","Y4","Y5"], y=fcfs2, text=[f"{x:,.0f}" for x in fcfs2], textposition="outside"))
        fig.update_layout(title="Forecast FCF", height=330, margin=dict(l=10,r=10,t=45,b=10), yaxis_title="₹ crore")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("### DCF Summary")
        st.write(f"Present Value of FCF: **₹{sum(pvs2):,.0f} cr**")
        st.write(f"PV of Terminal Value: **₹{pvtv2:,.0f} cr**")
        st.write(f"Enterprise Value: **₹{ev2:,.0f} cr**")
        st.write(f"Cash & Investments: **₹{cash:,.0f} cr**")
        st.write(f"Debt: **₹{debt:,.0f} cr**")
        st.success(f"Equity Value: ₹{eq2:,.0f} cr\n\nValue / Share: ₹{dcf2:,.0f}")

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">2. Comparable Companies</div>', unsafe_allow_html=True)
    edited = st.data_editor(peer_data, num_rows="dynamic", use_container_width=True, hide_index=True)
    vals = pd.to_numeric(edited["EV/EBITDA (x)"], errors="coerce").dropna()
    med = vals.median()
    comp_ev2 = p["ebitda"] * med
    comp_eq2 = comp_ev2 + cash - debt
    comp_ps2 = comp_eq2 / shares
    a,b,c = st.columns(3)
    a.metric("Median EV/EBITDA", f"{med:.2f}x")
    b.metric("Equity Value", f"₹{comp_eq2:,.0f} cr")
    c.metric("Value / Share", f"₹{comp_ps2:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">3. Precedent Transactions</div>', unsafe_allow_html=True)
    txe = st.data_editor(tx_data, num_rows="dynamic", use_container_width=True, hide_index=True)
    txvals = pd.to_numeric(txe["EV/EBITDA (x)"], errors="coerce").dropna()
    txmed = txvals.median()
    txev2 = p["ebitda"] * txmed
    txeq2 = txev2 + cash - debt
    txps2 = txeq2 / shares
    a,b,c = st.columns(3)
    a.metric("Median Transaction Multiple", f"{txmed:.2f}x")
    b.metric("Equity Value", f"₹{txeq2:,.0f} cr")
    c.metric("Value / Share", f"₹{txps2:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[3]:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">4. Asset-Based Valuation</div>', unsafe_allow_html=True)
    a,b,c = st.columns(3)
    assets_in = a.number_input("Total assets (₹ crore)", value=float(assets))
    liabilities_in = b.number_input("Total liabilities (₹ crore)", value=float(liabilities))
    adjustment = c.number_input("Fair-value adjustment (₹ crore)", value=0.0)
    nav = assets_in - liabilities_in + adjustment
    navps = nav / shares
    x,y = st.columns(2)
    x.metric("Net Asset Value", f"₹{nav:,.0f} cr")
    y.metric("Value / Share", f"₹{navps:,.0f}")
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[4]:
    summary = pd.DataFrame({
        "Method": ["DCF", "Comparable Companies", "Precedent Transactions", "Asset-Based"],
        "Value / Share": [dcf2, comp_ps2, txps2, navps]
    })
    if market_price > 0:
        summary["vs Market %"] = (summary["Value / Share"] / market_price - 1) * 100
    st.dataframe(
        summary.style.format({"Value / Share":"₹{:,.0f}", "vs Market %":"{:+.1f}%"}),
        use_container_width=True,
        hide_index=True
    )
    fig = go.Figure(go.Bar(
        x=summary["Method"], y=summary["Value / Share"],
        text=[f"₹{x:,.0f}" for x in summary["Value / Share"]],
        textposition="outside"
    ))
    if market_price > 0:
        fig.add_hline(y=market_price, line_dash="dash", annotation_text=f"Market ₹{market_price:,.0f}")
    fig.update_layout(title="Four-Model Valuation Comparison", height=420, yaxis_title="₹ / Share")
    st.plotly_chart(fig, use_container_width=True)

    st.download_button(
        "⬇️ Download valuation summary (CSV)",
        summary.to_csv(index=False).encode("utf-8"),
        "valuation_summary.csv",
        "text/csv"
    )

st.markdown("<br>", unsafe_allow_html=True)
st.caption("Educational valuation tool. Verify financial data, accounting definitions, peer selection and assumptions independently before using outputs.")
