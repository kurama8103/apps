# %%
import os
import pandas as pd
import pandas_datareader.data as web
import plotly.express as px
import streamlit as st

px.defaults.template = "plotly"
px.defaults.width = 600
px.defaults.height = 300
import matplotlib.pyplot as plt

# pd.options.plotting.backend = "plotly"

end = pd.Timestamp.today() + pd.Timedelta(days=0)
n = 365
start = end - pd.Timedelta(days=n + 1)
start_3y = end - pd.Timedelta(days=n * 3 + 1)
legend_dict = dict(
    x=0.5,
    y=1,
    yanchor="bottom",
    xanchor="center",
    orientation="h",
)
fn_fred_econ = "files/_fred_econ.pickle"
fn_fred_econ = "_fred_econ.pickle"

dic_ticker = {
    "US_FED_RATE": "DFF",
    "US_Govt_10Y": "DGS10",
    "USDJPY": "DEXJPUS",
    "USDEUR": "DEXUSEU",
    # "USDCNY": "DEXCHUS",
    "NASDAQ_Composit": "NASDAQCOM",
    # "SP500_VIX_3M": "VXVCLS",
    # "225": "NIKKEI225",
    "BTC_CB": "CBBTCUSD",
    # }
    # dic_ticker["M"] = {
    # "US_CPI_Core": "CPILFESL",
    "US_CPI": "CPIAUCSL",
    # "JP_CPI": "CPALTT01JPM661S",
    "JP_CPI": "CPALCY01JPM661N",
    "DE_CPI": "DEUCPALTT01IXOBSAM",
    "US_UNEMP": "UNRATE",
    "JP_UNEMP": "LRUNTTTTJPM156S",
    "DE_UNEMP": "LMUNRRTTDEM156S",
    # }
    # dic_ticker["Q"] = {
    "US_GDP_REAL": "GDPC1",
    "JP_GDP_REAL": "JPNRGDPEXP",
    "DE_GDP_REAL": "CLVMNACSCAB1GQDE",
    # "CN_GDP_REAL": "NGDPRXDCCNA",
    "US_GDP_NOMINAL": "GDP",
    "JP_GDP_NOMINAL": "JPNNGDP",
    "DE_GDP_NOMINAL": "CPMNACSCAB1GQDE",
    "Dollar_Index": "DTWEXBGS",
}


@st.cache_data(show_spinner=False)
def get_data_econ(fn: str, dic_ticker: dict, start, end, flg: bool = False):
    if os.path.exists(fn) and not (flg):
        print("read pickle")
        df = pd.read_pickle(fn)
    else:
        print("download from fred")
        df = web.DataReader(dic_ticker.values(), "fred", start, end)
        df.columns = dic_ticker.keys()
        df.to_pickle(fn)
    return df


def st_plot(
    df: pd.DataFrame,
    indexation: bool = False,
    round: int = 2,
    title: str = "",
    mode="plotly",
):
    if df is None:
        print("None")
        return None

    # df = df.dropna(how="all")
    if indexation:
        df /= df.iloc[0]
        title += " (Indexed)"

    if mode == "plotly":
        return st.plotly_chart(
            px.line(df.round(round), title=title).update_layout(legend=legend_dict),
            use_container_width=True,
        )
    else:
        fig, ax = plt.subplots(tight_layout=False)
        # ax.plot(df)
        df.plot(subplots=True, ax=ax)
        ax.legend(df.columns)
        return st.pyplot(fig)


# main
st.write("### econ data")

df_fred = get_data_econ(fn_fred_econ, dic_ticker, start_3y, end, flg=False)
s = df_fred.index[0].to_pydatetime()
e = df_fred.index[-1].to_pydatetime()
t = st.slider("", s, e, (s, e))
_d = df_fred[t[0] : t[1]]
st_plot(
    _d.loc[:, _d.columns.str.contains("NOMINAL")].dropna(how="all").pct_change(),
    indexation=False,
    round=3,
    title="NOMINAL GDP (QoQ)",
)
st_plot(
    _d.loc[:, _d.columns.str.contains("NOMINAL")].dropna(how="all"),
    indexation=True,
    round=3,
    title="NOMINAL GDP",
)
st_plot(
    _d.loc[:, _d.columns.str.contains("REAL")].dropna(how="all").pct_change(),
    indexation=False,
    round=3,
    title="REAL GDP (QoQ)",
)
st_plot(
    _d.loc[:, _d.columns.str.contains("REAL")].dropna(how="all"),
    indexation=True,
    round=3,
    title="REAL GDP",
)
df_ = pd.DataFrame(
    [
        (_d.loc[:, s + "_GDP_NOMINAL"] / _d.loc[:, s + "_GDP_REAL"])
        for s in ["US", "JP", "DE"]
    ]
).T.dropna(how="all")
df_.columns = [s + "_GDP_DFEFLATOR" for s in ["US", "JP", "DE"]]
st_plot(
    df_.pct_change(),
    indexation=False,
    round=3,
    title="GDP DEFLATOR (QoQ)",
)
st_plot(
    df_,
    indexation=True,
    round=3,
    title="GDP DEFLATOR",
)

# _d = dic_fred["M"]
# st_plot(
#     _d.loc[:, _d.columns.str.contains("CPI")],
#     indexation=True,
#     round=3,
#     title="CPI",
# )
# st_plot(_d.loc[:, _d.columns.str.contains("UNEMP")], title="Unemployment")

st_plot(_d.get(["US_FED_RATE", "US_Govt_10Y"]), title="US Interest rate")
st_plot(_d.get(["Dollar_Index", "USDJPY", "USDEUR"]), indexation=True, title="Currency")
# st_plot(
#     _d.get(["NASDAQ_Composit", "BTC_CB"]),
#     indexation=True,
#     title="Indices",
# )
st.write(
    "Source :  \n"
    + "Federal Reserve Bank of St. Louis, "
    + "Organization for Economic Co-operation and Development, "
    + "Board of Governors of the Federal Reserve System (US), "
    + "U.S. Bureau of Economic Analysis, "
    # + "U.S. Bureau of Labor Statistics, "
    # + "NASDAQ OMX Group, Inc., "
    # + "Coinbase, "
    + "JP. Cabinet Office, "
    + "Eurostat"
)


# %%
