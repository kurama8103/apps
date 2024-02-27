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
    if uploaded_file is None:
        if "df" in st.session_state:
            return st.session_state["df"]
        else:
            print(sys.argv)
            # uploaded_file = sys.argv[1]
    else:
        df = pd.read_csv(uploaded_file, index_col=0, parse_dates=True)
        st.session_state["df"] = df
        return df


def momentum(x, window=None):
    if window == None:
        window = len(x)
    r = np.cumprod(x[-window - 2 : -1] + 1)
    mom = r[-1] / r[0] - 1
    return x[-1] - mom


def moving_window(x, window: int, func) -> list:
    return [func(d) for d in sliding_window_view(x, window)]


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
        "S&P500": "SP500",
        "NASDAQ_Composit": "NASDAQCOM",
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
