import streamlit as st
import pandas as pd

def load_csv():
    """_summary_
    _extended_summary_

    Returns:
        _type_: _description_
    """
    uploaded_file = st.file_uploader(
        "choose your csv file",
        type=["csv"],
        key="main",
    )
    if uploaded_file:
        return pd.read_csv(uploaded_file, index_col=0, parse_dates=True)
    else:
        return None

def moving_window_df(df, window, func):
    d = {}
    if len(df) > window:
        for i, idx in enumerate(df.index):
            if i > window:
                _ = df.iloc[i - window : i]
                d[idx] = func(_)

        return pd.DataFrame(d).T
    else:
        return None

def format_df(df):
    return df.style.format("{:.2%}")
