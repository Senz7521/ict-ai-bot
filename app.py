import streamlit as st

selected_pair = st.selectbox(
    "SELECT PAIR",
    [
        "BTC/USDT",
        "ETH/USDT"
    ]
)

st.success(f"ACTIVE PAIR: {selected_pair}")


st.success(f"ACTIVE PAIR: {selected_pair}")
import streamlit as st
# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="ICT AI BOT",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("ICT AI BOT")

st.markdown("---")

# =========================================================
# HTF SECTION
# =========================================================

st.header("HTF ANALYSIS")

col1, col2 = st.columns(2)

with col1:

    st.subheader("HTF BIAS")

    st.success("""
    BULLISH

    • Bullish Structure  
    • External Liquidity Taken  
    • Strong Displacement
    """)

with col2:

    st.subheader("HTF POI")

    st.info("""
    BULLISH ORDER BLOCK

    Zone:
    104200 - 104350
    """)

st.markdown("---")

# =========================================================
# LTF SECTION
# =========================================================

st.header("LTF CONFIRMATION")

col3, col4 = st.columns(2)

with col3:

    st.subheader("LIQUIDITY SWEEP")

    st.warning("""
    BUY SIDE SWEEP

    • Internal Liquidity Taken
    • Rejection Confirmed
    """)

    st.subheader("MSS")

    st.success("""
    BULLISH MSS

    • Strong Close Above Structure
    • Displacement Confirmed
    """)

with col4:

    st.subheader("FVG / OB")

    st.info("""
    BULLISH FVG

    Entry Zone:
    104120 - 104180
    """)

    st.subheader("ENTRY")

    st.success("""
    BUY BTC

    Entry: 104150
    SL: 103950
    TP1: 104500
    TP2: 104900
    RR: 1:3
    """)

st.markdown("---")

# =========================================================
# FOOTER
# =========================================================

st.caption("ICT AI BOT PRO")