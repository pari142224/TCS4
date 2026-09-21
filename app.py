import streamlit as st
import pandas as pd

st.set_page_config(page_title="4-Model Business Valuation Calculator", layout="wide")
st.title("📊 Business Valuation Calculator — 4 Models")
st.caption("DCF • Comparable Companies • Precedent Transactions • Asset-Based Valuation")

st.sidebar.header("1) Company Inputs")
shares = st.sidebar.number_input("Shares outstanding (crore)", value=361.81, min_value=0.01)
cash = st.sidebar.number_input("Cash + investments / excess financial assets (₹ crore)", value=50079.0, min_value=0.0)
debt = st.sidebar.number_input("Interest-bearing debt (₹ crore)", value=0.0, min_value=0.0)

tab1, tab2, tab3, tab4 = st.tabs(["DCF", "Comparable Companies", "Precedent Transactions", "Asset-Based"])

with tab1:
    st.header("1. DCF Valuation")
    st.write("FCFF/FCF-based simplified DCF. Enter your own assumptions; no investment recommendation is made.")

    c1, c2, c3 = st.columns(3)
    fcf0 = c1.number_input("Base-year FCF (₹ crore)", value=48424.0, min_value=0.0)
    wacc = c2.number_input("WACC (%)", value=10.0, min_value=0.1, max_value=50.0) / 100
    tg = c3.number_input("Terminal growth (%)", value=3.5, min_value=0.0, max_value=9.9) / 100

    st.subheader("FCF growth assumptions")
    default_growth = [7.0, 7.0, 6.0, 5.0, 4.0]
    growth = []
    cols = st.columns(5)
    for i in range(5):
        growth.append(cols[i].number_input(f"Year {i+1} (%)", value=default_growth[i], key=f"g{i}") / 100)

    fcfs, pvs = [], []
    prev = fcf0
    for i, g in enumerate(growth, 1):
        f = prev * (1 + g)
        fcfs.append(f)
        pvs.append(f / ((1 + wacc) ** i))
        prev = f

    terminal = fcfs[-1] * (1 + tg) / (wacc - tg) if wacc > tg else float("nan")
    pv_terminal = terminal / ((1 + wacc) ** 5)
    enterprise = sum(pvs) + pv_terminal
    equity = enterprise + cash - debt
    per_share = equity / shares

    df = pd.DataFrame({
        "Year": [1,2,3,4,5],
        "Growth": [f"{x:.1%}" for x in growth],
        "FCF (₹ cr)": fcfs,
        "PV of FCF (₹ cr)": pvs
    })
    st.dataframe(df, use_container_width=True)
    a,b,c,d = st.columns(4)
    a.metric("PV of explicit FCF", f"₹{sum(pvs):,.0f} cr")
    b.metric("PV of terminal value", f"₹{pv_terminal:,.0f} cr")
    c.metric("Equity value", f"₹{equity:,.0f} cr")
    d.metric("DCF value/share", f"₹{per_share:,.2f}")

with tab2:
    st.header("2. Comparable Companies")
    st.write("Enter peer EV/EBITDA multiples and the target company's EBITDA.")
    ebitda = st.number_input("Target EBITDA (₹ crore)", value=76800.0, min_value=0.0, key="comp_ebitda")
    n = st.number_input("Number of peers", min_value=1, max_value=20, value=4, step=1)
    mults = []
    for i in range(int(n)):
        mults.append(st.number_input(f"Peer {i+1} EV/EBITDA (x)", value=[9.7,11.7,7.6,10.6][i] if i < 4 else 10.0, min_value=0.1, key=f"m{i}"))
    median = float(pd.Series(mults).median())
    ev = ebitda * median
    equity = ev + cash - debt
    per_share = equity / shares
    a,b,c = st.columns(3)
    a.metric("Median multiple", f"{median:.2f}x")
    b.metric("Equity value", f"₹{equity:,.0f} cr")
    c.metric("Comparable value/share", f"₹{per_share:,.2f}")
    st.dataframe(pd.DataFrame({"Peer": range(1,int(n)+1), "EV/EBITDA (x)": mults}), use_container_width=True)

with tab3:
    st.header("3. Precedent Transactions")
    st.write("Enter transaction EV/EBITDA multiples from comparable acquisitions.")
    tx_ebitda = st.number_input("Target EBITDA (₹ crore)", value=76800.0, min_value=0.0, key="tx_ebitda")
    n2 = st.number_input("Number of transactions", min_value=1, max_value=20, value=4, step=1)
    tx_mults = []
    for i in range(int(n2)):
        tx_mults.append(st.number_input(f"Transaction {i+1} EV/EBITDA (x)", value=[8.8,10.4,9.5,11.0][i] if i < 4 else 10.0, min_value=0.1, key=f"tx{i}"))
    tx_median = float(pd.Series(tx_mults).median())
    tx_ev = tx_ebitda * tx_median
    tx_equity = tx_ev + cash - debt
    tx_per_share = tx_equity / shares
    a,b,c = st.columns(3)
    a.metric("Median transaction multiple", f"{tx_median:.2f}x")
    b.metric("Equity value", f"₹{tx_equity:,.0f} cr")
    c.metric("Transaction value/share", f"₹{tx_per_share:,.2f}")
    st.dataframe(pd.DataFrame({"Transaction": range(1,int(n2)+1), "EV/EBITDA (x)": tx_mults}), use_container_width=True)

with tab4:
    st.header("4. Asset-Based Valuation")
    assets = st.number_input("Total assets (₹ crore)", value=182372.0, min_value=0.0)
    liabilities = st.number_input("Total liabilities (₹ crore)", value=75800.0, min_value=0.0)
    adjusted_assets = st.number_input("Optional fair-value adjustment to assets (₹ crore)", value=0.0)
    adjusted_liabilities = st.number_input("Optional adjustment to liabilities (₹ crore)", value=0.0)
    net_assets = (assets + adjusted_assets) - (liabilities + adjusted_liabilities)
    bvps = net_assets / shares
    a,b = st.columns(2)
    a.metric("Net asset value", f"₹{net_assets:,.0f} cr")
    b.metric("Asset-based value/share", f"₹{bvps:,.2f}")

st.divider()
st.caption("Educational calculator. Verify source data, accounting definitions, peer selection, and valuation assumptions before using results.")
