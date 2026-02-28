"""Data Explorer page sample."""

import pandas as pd
import streamlit as st

st.title("Data Explorer")
st.write("データを確認するためのサンプルページです。")

sample_df = pd.DataFrame(
    {
        "category": ["A", "B", "C", "D"],
        "value": [12, 28, 19, 34],
    }
)

st.dataframe(sample_df, use_container_width=True)
st.bar_chart(sample_df.set_index("category"))
