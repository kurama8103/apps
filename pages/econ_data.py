# %%
import os
import pickle
import pandas as pd
import pandas_datareader.data as web
import plotly.express as px
import streamlit as st

px.defaults.template = "plotly"
px.defaults.width = 600
px.defaults.height = 300
# import matplotlib.pyplot as plt
# pd.options.plotting.backend = "plotly"

end = pd.Timestamp.today() + pd.Timedelta(days=0)
start = end - pd.Timedelta(days=366)
start_3y = end - pd.Timedelta(days=365 * 3 + 1)
legend_dict = dict(
    x=0.5,
    y=1,
    yanchor="bottom",
    xanchor="center",
    orientation="h",
)
fn = "dic_fred.pickle"

# %%
dic_ticker = {}
dic_ticker["D"] = {
    "US_FED_RATE": "DFF",
    "USG10": "DGS10",
    "USDJPY": "DEXJPUS",
    "USDEUR": "DEXUSEU",
    # "USDCNY": "DEXCHUS",
    "SP500": "SP500",
    "SP500_VIX_3M": "VXVCLS",
    # "225": "NIKKEI225",
    "BTC_CB": "CBBTCUSD",
}
dic_ticker["M"] = {
    # "US_CPI_Core": "CPILFESL",
    "US_CPI": "CPIAUCSL",
    # "JP_CPI": "CPALTT01JPM661S",
    "JP_CPI": "CPALCY01JPM661N",
    "DE_CPI": "DEUCPALTT01IXOBSAM",
    "US_UNEMP": "UNRATE",
    "JP_UNEMP": "LRUNTTTTJPM156S",
    "DE_UNEMP": "LMUNRRTTDEM156S",
}
dic_ticker["Q"] = {
    "US_GDP_REAL": "GDPC1",
    "JP_GDP_REAL": "JPNRGDPEXP",
    "DE_GDP_REAL": "CLVMNACSCAB1GQDE",
    # "CN_GDP_REAL": "NGDPRXDCCNA",
    "US_GDP_NOMINAL": "GDP",
    "JP_GDP_NOMINAL": "JPNNGDP",
    "DE_GDP_NOMINAL": "CPMNACSCAB1GQDE",
}


# %%
@st.cache(allow_output_mutation=True, show_spinner=False)
def get_data_econ(fn: str, dic_ticker: dict, start, end, flg: bool = False):
    if os.path.exists(fn) and not (flg):
        print("load")
        with open(fn, "rb") as f:
            dic_fred = pickle.load(f)

    else:
        print("download")
        if "dic_fred" not in locals():
            dic_fred = {}

        for k in dic_ticker.keys():
            type_ = k
            _d = web.DataReader(dic_ticker[type_].values(), "fred", start, end)
            _d.columns = dic_ticker[type_].keys()
            dic_fred[type_] = _d

        with open(fn, "wb") as f:
            pickle.dump(dic_fred, f)

    return dic_fred


def st_plot(df, indexation: bool = False, round: int = 2, title: str = ""):
    if indexation:
        df /= df.iloc[0]
        title += " (Indexed)"

    # fig, ax = plt.subplots()
    # ax.plot(df)
    # ax.legend(df.columns)
    # return st.pyplot(fig)

    return st.plotly_chart(
        px.line(df.round(round), title=title).update_layout(legend=legend_dict),
        use_container_width=True,
    )


def main(dic_fred):
    st.write("### econ data")
    _d = dic_fred["Q"]
    st_plot(
        _d.loc[:, _d.columns.str.contains("NOMINAL")],
        indexation=True,
        round=3,
        title="NOMINAL GDP",
    )
    st_plot(
        _d.loc[:, _d.columns.str.contains("REAL")],
        indexation=True,
        round=3,
        title="REAL GDP",
    )

    _d = dic_fred["M"]
    st_plot(
        _d.loc[:, _d.columns.str.contains("CPI")],
        indexation=True,
        round=3,
        title="CPI",
    )
    st_plot(
        _d.loc[:, _d.columns.str.contains("UNEMP")],
        title="Unemployment",
    )

    # fig, ax = plt.subplots(tight_layout=False)
    # dic_fred["D"].plot(subplots=True, ax=ax)
    # st.pyplot(fig)

    st_plot(dic_fred["D"][["US_FED_RATE", "USG10"]], title="US Interest rate")
    st_plot(dic_fred["D"][["USDJPY", "USDEUR"]], indexation=True, title="FX rate")
    st_plot(dic_fred["D"][["SP500", "BTC_CB"]], indexation=True, title="Indices")
    st_plot(dic_fred["D"][["SP500_VIX_3M"]], title="SP500_VIX_3M")


dic_fred = get_data_econ(fn, dic_ticker, start_3y, end, flg=False)
main(dic_fred=dic_fred)
# %%
