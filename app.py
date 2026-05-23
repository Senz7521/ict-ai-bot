import streamlit as st

st.set_page_config(
    page_title="ICT AI BOT PRO",
    layout="wide"
)

# =========================
# TITLE
# =========================

st.title("ICT AI BOT PRO")

st.markdown("---")

# =========================
# HTF SECTION
# =========================

col1, col2 = st.columns(2)

with col1:
    st.markdown("## HTF BIAS")
    st.success("BULLISH")

with col2:
    st.markdown("## HTF POI")
    st.info("BULLISH ORDER BLOCK")

st.markdown("---")

# =========================
# POI TAP
# =========================

st.markdown("## HTF POI TAP")

tap_box = st.container(border=True)

with tap_box:
    st.warning("PRICE TOUCHED HTF POI")

st.markdown("---")

# =========================
# LTF CONFIRMATION
# =========================

st.markdown("## LTF CONFIRMATION")

col3, col4 = st.columns(2)

with col3:
    box1 = st.container(border=True)

    with box1:
        st.markdown("### LTF MSS")
        st.success("BULLISH MSS CONFIRMED")

with col4:
    box2 = st.container(border=True)

    with box2:
        st.markdown("### LTF POI")
        st.info("FVG TAP CONFIRMED")

st.markdown("---")

# =========================
# MICRO MSS
# =========================

st.markdown("## MICRO MSS ENTRY")

micro_box = st.container(border=True)

with micro_box:
    st.success("MICRO MSS CONFIRMED")

st.markdown("---")

# =========================
# ENTRY MODEL
# =========================

st.markdown("## ENTRY MODEL")

entry_col1, entry_col2, entry_col3 = st.columns(3)

with entry_col1:
    st.metric("ENTRY", "BUY")

with entry_col2:
    st.metric("STOP LOSS", "5 POINTS")

with entry_col3:
    st.metric("TAKE PROFIT", "15 POINTS")

st.markdown("---")

# =========================
# FOOTER
# =========================

st.caption("ICT AI BOT PRO")