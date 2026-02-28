"""Settings page sample."""

import streamlit as st

st.title("Settings")
st.write("アプリの設定値を管理するページのテンプレートです。")

with st.form("settings_form"):
    environment = st.selectbox("Environment", ["development", "staging", "production"])
    notify = st.checkbox("通知を有効化", value=True)
    submitted = st.form_submit_button("保存")

if submitted:
    st.success(f"設定を保存しました: env={environment}, notify={notify}")
