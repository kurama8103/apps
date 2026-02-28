"""Top page for the Streamlit dashboard application."""

from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Dashboard Index", page_icon="📊", layout="wide")

st.title("📊 Dashboard Index")
st.write(
    "複数ページで機能を拡張できる Streamlit ダッシュボードのトップページです。"
)

st.markdown("## 利用可能なページ")

pages_dir = Path(__file__).parent / "pages"
page_files = sorted(
    page for page in pages_dir.glob("*.py") if page.name != "__init__.py"
)

if not page_files:
    st.info("まだページがありません。`pages/` 配下に追加してください。")
else:
    for page in page_files:
        page_name = page.stem.split("_", 1)[-1].replace("_", " ")
        st.markdown(f"- **{page_name}** (`pages/{page.name}`)")

st.markdown("---")
st.caption("新しい機能は `pages/` 配下にファイルを追加して拡張してください。")
