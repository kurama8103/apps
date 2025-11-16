import pandas as pd
import streamlit as st
import sys
import pandas_datareader.data as web
import os
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view
import io
import csv

fn_fred = "files/fred_indices.pickle"


def load_csv():
    s = "Choose a CSV file. "
    s += "The first column of the file is the date, the first row is the column name."

    uploaded_file = st.file_uploader(
        s,
        type="csv",
    )
    if "sample" not in st.session_state:
        st.session_state["sample"] = False
    if "df" not in st.session_state:
        st.session_state["df"] = None

    if st.checkbox("Use sample data", value=st.session_state["sample"]):
        st.session_state["str"] = "source: Currency data from FRED"
        st.session_state["df"] = get_indices_fred(fn_fred, False)
        st.session_state["sample"] = True
    else:
        st.session_state["sample"] = False

    if uploaded_file is not None:
        st.session_state["sample"] = False
        st.session_state["str"] = "source: " + uploaded_file.name
        st.session_state["df"] = pd.read_csv(
            uploaded_file, index_col=0, parse_dates=True
        )

    # st.session_state["flg_pct"] = False
    # if flg_pct:
    #     if st.checkbox("Use percentage change (return) data", flg_pct):
    #         df_ = df_.pct_change().dropna()
    #         st.session_state["flg_pct"]=True
    #     else:
    #         st.session_state["flg_pct"] = False
    # st.write(st.session_state["flg_pct"])
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


@st.cache_data()
def get_indices_fred(path_pickel: str, force_download: bool = False) -> pd.DataFrame:
    end = pd.Timestamp.today() + pd.Timedelta(days=0)
    start = pd.to_datetime("2020-01-01")
    dic_ticker = {
        # "S&P500": "SP500",
        # "NASDAQ_Composit": "NASDAQCOM",
        # "US_10Y_interest_rate":"REAINTRATREARAT10Y",
        "USDJPY": "DEXJPUS",
        "EURUSD": "DEXUSEU",
        "USDCHY": "DEXCHUS",
    }
    if os.path.exists(path_pickel) and not (force_download):
        print("load")
        df = pd.read_pickle(path_pickel)

    else:
        print("download")
        df = web.DataReader(dic_ticker.values(), "fred", start, end)
        df.columns = dic_ticker.keys()
        df.to_pickle(path_pickel)

    return df


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


def class_to_csv(class_):
    import csv
    import io

    f = io.StringIO()
    writer = csv.DictWriter(f, fieldnames=class_.__dict__.keys())
    writer.writeheader()
    writer.writerow(class_.__dict__)
    return f


def flg_use_pct(df, checkbox_flg=True):
    flg_pct = False
    if st.checkbox("Use percentage change (return) data", checkbox_flg):
        df = df.pct_change().dropna()
        flg_pct = True
    return df, flg_pct


def multiselect_X_y(df):
    target = st.selectbox("select target", df.columns)
    features = st.multiselect(
        "select features",
        list(df.columns.drop(target)),
        default=list(df.columns.drop(target)),
    )
    y = df[target]
    X = df[features]
    return X, y
