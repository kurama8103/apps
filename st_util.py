# %%
# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import sys
import pandas_datareader.data as web
import os
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

fn_fred = "files/fred_indices.pickle"


def load_csv():
    s = "Choose a CSV file. "
    s += "The first column of the file is the date, the first row is the column name."

    uploaded_file = st.file_uploader(
        s,
        type="csv",
    )
    if 'sample' not in st.session_state:
        st.session_state['sample'] = False
    if 'df' not in st.session_state:
        st.session_state['df'] = None

    if st.checkbox("Use sample data", value=st.session_state["sample"]):
        st.session_state["str"] = "source: Currency data (USDJPY and USDEUR) from FRED"
        st.session_state["df"] = get_indices(False)
        st.session_state["sample"] = True
    else:
        st.session_state["sample"] = False

    if uploaded_file is not None:
        st.session_state["sample"] = False
        st.session_state["str"] = "source: " + uploaded_file.name
        st.session_state["df"] = pd.read_csv(
            uploaded_file, index_col=0, parse_dates=True
        )

    if "str" in st.session_state:
        st.subheader(st.session_state["str"])
    return st.session_state["df"]

    # st.header("US Macroeconomic Data from FRED")
    # st.json({
    #     "realgdp": "Real gross domestic product",
    #     "realcons": "Real personal consumption expenditures",
    #     "realinv" :"Real gross private domestic investment",
    #     "realgovt":"Real federal consumption expenditures & gross investment",
    #     "realdpi": "Real private disposable income",
    #     "cpi" :"Consumer price index",
    #     "m1": "M1 nominal money stock",
    #     "tbilrate": "3-monthtreasury bill",
    #     "unemp" :"Unemployment rate",
    #     "pop":"Population",
    #     "infl":"Inflation rate (cpi base)",
    #     "realint":"Real interest rate (tbilrate - infl)"
    #     })
    # df = pd.concat([load_test_data()[1], load_test_data()[0]], axis=1)


def momentum(x, window=None):
    if window == None:
        window = len(x)
    r = np.cumprod(x[-window - 2 : -1] + 1)
    mom = r[-1] / r[0] - 1
    return x[-1] - mom


def moving_window(x, window: int, func) -> list:
    return [func(d) for d in sliding_window_view(x, window, axis=0)]


def moving_window_df(x: pd.DataFrame, window: int, func) -> pd.DataFrame:
    try:
        return pd.DataFrame(
            moving_window(x.values, window, func),
            index=x.tail(len(x) + 1 - window).index,
        )
    except:
        return None


def format_df(df, digit=4):
    df = df.round(digit)
    df.index = df.index.astype(str)
    return df


def get_indices(flg: bool = False) -> pd.DataFrame:
    end = pd.Timestamp.today() + pd.Timedelta(days=0)
    start = pd.to_datetime("2020-01-01")
    dic_ticker = {
        # "S&P500": "SP500",
        # "NASDAQ_Composit": "NASDAQCOM",
        # "US_10Y_interest_rate":"REAINTRATREARAT10Y",
        "USDJPY": "DEXJPUS",
        "USDEUR": "DEXUSEU",
    }
    if os.path.exists(fn_fred) and not (flg):
        print("load")
        df = pd.read_pickle(fn_fred)

    else:
        print("download")

    df = web.DataReader(dic_ticker.values(), "fred", start, end)
    df.columns = dic_ticker.keys()

    df.to_pickle(fn_fred)
    return df


# @st.cache(show_spinner=True, allow_output_mutation=True)
# def predict_darts(series, n_pred=10, w=20):
#     from darts.models import NaiveDrift, NaiveSeasonal, ExponentialSmoothing
#     from darts.models import RandomForest, RegressionModel, AutoARIMA, Prophet
#     from darts import TimeSeries

#     train = TimeSeries.from_series(series)[-w:]

#     models = [
#         # NaiveDrift(n_pred),
#         NaiveSeasonal(n_pred),
#         AutoARIMA(),
#         # ExponentialSmoothing(),
#         # Prophet(),
#         # RandomForest(lags=5),
#         RegressionModel(lags=5),
#     ]

#     pred = pd.DataFrame()
#     for model in models:
#         p_ = model.fit(series=train).predict(n_pred).pd_series()
#         s = str(model)
#         if s.find("(") > 0:
#             s = s[: s.find("(")]
#         p_.name = s
#         pred = pd.concat([pred, p_], axis=1)
#     pred.index = pd.to_datetime(pred.index)
#     return pred

# import statsmodels.api as sm

# models = {
#     "UnobservedComponents": sm.tsa.UnobservedComponents(
#         dfr, "local linear trend", cycle=True
#     ),
#     "SARIMAX": sm.tsa.SARIMAX(dfr, order=(5, 1, 5)),
# }
# for k, v in models.items():
#     res = v.fit()
#     pred[k] = res.forecast(n_pred)

# pred["mean"] = pred.mean(axis=1)
# pred = pd.concat([dfr.tail(20), pred], axis=1)

# if st.checkbox("cumulative"):
#     d_ = (pred + 1).cumprod()
#     d_.iloc[:, 0] = d_.iloc[:, 0] / (d_.iloc[:, 0].dropna()[-1])
# else:
#     d_ = pred
# st.line_chart(d_, height=h)
# st.dataframe(format_df(d_))

import unicodedata

url_unit = "https://www.jpx.co.jp/equities/products/etfs/base-price/nlsgeu0000051wtj-att/202401_etfs.xlsx"
url_close = "https://www.jpx.co.jp/markets/statistics-equities/price/skc8fn0000001vzu-att/ivt_202401.xlsx"
url_des = "https://www.jpx.co.jp/equities/products/etfs/issues/01.html"
fn_etf = "files/etf.csv"
fn_etf_p = "files/etf_summary.pickel"


def get_unit_close():
    if os.path.exists(fn_etf):
        df_m = pd.read_csv(fn_etf, index_col=0)
    else:
        print("download excels")
        df_unit = pd.read_excel(url_unit, index_col="コード")
        df_unit.index = df_unit.index.astype(str, copy=False)
        df_close = pd.read_excel(url_close, index_col=1, skiprows=[0, 1, 2, 4, 5])
        df_close["始値"] = pd.to_numeric(df_close["始値"], errors="coerce")
        df_close["高値"] = pd.to_numeric(df_close["高値"], errors="coerce")
        df_close["安値"] = pd.to_numeric(df_close["安値"], errors="coerce")
        df_close["終値"] = pd.to_numeric(df_close["終値"], errors="coerce")
        df_close["終値平均"] = pd.to_numeric(df_close["終値平均"], errors="coerce")

        df_m = pd.merge(
            df_close, df_unit, how="outer", left_index=True, right_index=True
        ).reset_index()
        df_m.to_csv(fn_etf)
    return df_m


def get_etf_des():
    print("download html")
    return pd.read_html(url_des, index_col=None)


def formater_etf_des(df):
    df_des = df[0].set_index("コード")

    df_des["AM"] = [
        unicodedata.normalize("NFKC", s[:-7]).replace("アセットマネジメント", "AM")
        for s in df_des["管理会社 （検索コード）"]
    ]
    df_des["type"] = [
        unicodedata.normalize("NFKC", s)
        .replace("(配当込み)", "")
        .replace("インデックス", "")
        .replace("指数", "")
        .replace("トータルリターン・", "株価")
        .replace("JPX 日経 400", "JPX日経400")
        .replace("東証 REIT ", "東証REIT")
        for s in df_des["連動対象指標"]
    ]
    df_des["offshore"] = [1 if "注2" in s else 0 for s in df_des["名称"]]
    df_des["offshore"].astype(int)
    return df_des


def create_etf_df() -> pd.DataFrame:
    df_m = get_unit_close()
    df_m.index.name = "code"

    df_g = df_m.groupby("code").last()
    df_g["vol"] = (
        pd.to_numeric(df_g["終値"], errors="coerce") * df_g["受益権口数"] / 1e8
    )

    if "df_" not in locals():
        df_ = get_etf_des()
    df_des = formater_etf_des(df_)
    df_s = pd.merge(df_g, df_des, how="outer", left_index=True, right_index=True)[
        [
            "銘柄名",
            "AM",
            "type",
            "offshore",
            "vol",
            # "終値",
            # "日付.4",
            # "受益権口数",
            # "銘柄属性",
            # "日付",
        ]
    ].dropna(subset="AM")
    df_s.to_pickle(fn_etf_p)
    return df_s


def read_eft_df(flg: bool = False):
    df = None
    if os.path.exists(fn_etf_p) and not (flg):
        print("read pickle")
        df = pd.read_pickle(fn_etf_p)
    else:
        df = create_etf_df()
    return df


def load_test_data():
    from statsmodels.datasets import macrodata

    df = macrodata.load()["data"]
    df.index = pd.date_range("1959-03-31", periods=len(df), freq="Q")
    df[["year", "quarter"]] = df[["year", "quarter"]].astype(int)
    df[df.columns.drop(["year", "quarter"])] = (
        df[df.columns.drop(["year", "quarter"])].ffill().pct_change()
    )
    df = df.replace([np.inf, -np.inf], np.nan).dropna()
    return df.drop("realgdp", axis=1), df["realgdp"]


# import os
def cd():
    print(os.getcwd())
    # os.chdir(os.path.dirname(__file__))
    # print(os.getcwd())


def calc_regression(df_, flg=0):
    y = st.selectbox("Y", df_.columns)
    c = list(df_.columns.drop(y))
    x = st.multiselect("X", c, c)
    if len(x) == 0:
        st.stop()

    model = LinearRegression(fit_intercept=True, normalize=False)
    res = summary_model_sk(model, df_[x], df_[y])
    st.write(model, res["score"])
    st.json(res, expanded=False)

    model = LassoCV(
        fit_intercept=True, normalize=False, alphas=[0, 0.01, 0.1, 1, 10], cv=5
    )
    res = summary_model_sk(model, df_[x], df_[y])
    st.write(model, res["score"])
    st.json(res, expanded=False)

    pred = (df_[x] * res["coef"]).sum(axis=1) + res["intercept"]
    pred.name = "prediction"
    pred = pd.concat([pred, df_[y]], axis=1)
    if flg == 1:
        pred = (1 + pred).cumprod()
    st.line_chart(pred, height=200)


def summary_model_sk(model, x, y):
    model.fit(x, y)
    res = {
        #        'model': model,
        "score": model.score(x, y),
        "intercept": model.intercept_,
        "coef": model.coef_.tolist(),
        #        'predict':model.predict(x),
        "params": model.get_params(),
    }
    return res
