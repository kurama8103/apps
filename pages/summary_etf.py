# %%
# import pandas as pd
import unicodedata
import plotly.express as px
import streamlit as st
from st_util import read_eft_df

### pd.options.plotting.backend = "plotly"


def proc_plotly(df):
    df = df.reset_index()
    df["vol"] /= 10000
    df["type"] = [s[:12] for s in df["type"]]
    df["銘柄名"] = [unicodedata.normalize("NFKC", str(s))[:20] for s in df["銘柄名"]]
    # df.set_index("銘柄名")
    return df


df_s = read_eft_df()
df_p = proc_plotly(df_s)
st.plotly_chart(
    px.bar(
        df_p.query("offshore==0").sort_values("vol", ascending=False).head(10).round(1),
        x="銘柄名",
        y="vol",
        hover_name="AM",
        title="時価総額(ファンド別)",
        hover_data={"銘柄名": None, "vol": None},
    )
)
st.plotly_chart(
    px.bar(
        df_p.query("offshore==0")
        .groupby("AM")
        .sum(numeric_only=True)
        .sort_values("vol", ascending=False)["vol"]
        .head(10)
        .round(1),
        y="vol",
        title="時価総額(運用会社別)",
        hover_data={"vol": None},
        hover_name=None,
    )
)
