"""Overview page sample."""

import streamlit as st

st.title("Overview")
st.write("ダッシュボードの全体サマリを表示するページです。")

col1, col2, col3 = st.columns(3)
col1.metric("Users", "1,024", "+8%")
col2.metric("Revenue", "¥1.2M", "+3.4%")
col3.metric("Errors", "12", "-15%")
