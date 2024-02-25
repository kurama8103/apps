# %%
# -*- coding: utf-8 -*-

import quantstats as qs
import pandas as pd
import numpy as np
import streamlit as st
import io
import os
import pandas_datareader.data as web
from numpy.lib.stride_tricks import sliding_window_view
from st_util import load_csv

# import myfunc.finfunc as mff


@st.cache(allow_output_mutation=True, show_spinner=False)
def get_indices(flg: bool = False):
    fn = "dic_fred.pickle"
    end = pd.Timestamp.today() + pd.Timedelta(days=0)
    start = pd.to_datetime("2020-01-01")
    dic_ticker = {
        "S&P500": "SP500",
        "NASDAQ_Composit": "NASDAQCOM",
    }
    if os.path.exists(fn) and not (flg):
        print("load")
        df = pd.read_pickle(fn)

    else:
        print("download")

    df = web.DataReader(dic_ticker.values(), "fred", start, end)
    df.columns = dic_ticker.keys()

    # df.to_pickel(fn)
    return df


def format_df(df, digit=4):
    df = df.round(digit)
    df.index = df.index.astype(str)
    return df


# def mape(pred, true):
#     return np.mean(np.abs((pred - true) / true)) * 100


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


@st.cache(show_spinner=False)
def qs_html(df: pd.DataFrame, download_filename, benchmark=None):
    qs.reports.html(
        df,
        # rf=0.0,
        title=df.name,
        download_filename=download_filename,
        output="./tmp/",
        benchmark=benchmark,
    )

    with open(download_filename) as f:
        s = f.read()

    return s


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


def _f(x):
    n = 252
    m = np.mean(x) * n
    s = np.std(x) * np.sqrt(n)
    d = {
        "rolling_return": m,
        "standard deviation": s,
        "sharpe ratio": (m / s),
        # "skew": scipy.stats.skew(x),
        # "kurt": scipy.stats.kurtosis(x),
        # "hurst": mff.hurst(x)[0],
        "momentum": momentum(x),
        # "cvar": mff.cvar(x)[1],
        # "adf":mff.adf_summary(x)['adf'],
        # "max_draw_down": np.cumprod(x + 1)[-1] / np.cumprod(x + 1).max() - 1,
    }
    return d


def tsa_render(df):
    h = 150
    window = 180
    qs.extend_pandas()
    if df is not None:
        st.markdown("### Input data")
        code = st.selectbox("select data", df.columns)
        st.line_chart(df[code], height=h)
        d1 = df.index[0].to_pydatetime()
        d2 = df.index[-1].to_pydatetime()
        d1, d2 = st.slider(
            "period",
            value=(d1, d2),
            min_value=d1,
            max_value=d2,
            format="Y/M/D",
            step=pd.Timedelta(days=1),
        )
        df_ = df[code].loc[d1:d2]

        if df_.min() < 0:
            pass
        else:
            dfr = df_.pct_change().fillna(0)
            dfr.name = "cumulative_return"

        # st.dataframe(dfr)
        st.text(
            # "From "
            # + df_.index[0].strftime("%Y-%m-%d")
            # + " To "
            # + df_.index[-1].strftime("%Y-%m-%d")
            # + "\n"
            ""
            + str((df_.index[-1] - df_.index[0]).days)
            + " days ("
            + str(round((df_.index[-1] - df_.index[0]).days / 365, 2))
            + " years)"
        )

        # fig = plt.figure(figsize=(8, 2))
        # dfr.hist(bins=20)
        # st.pyplot(fig)

        # met = qs.reports.metrics(dfr, display=False)
        # st.dataframe(
        #     (
        #         met.loc[
        #             [
        #                 # "Start Period",
        #                 # "End Period",
        #                 # "Risk-Free Rate",
        #                 "Cumulative Return",
        #                 "All-time (ann.)",
        #                 "CAGR﹪",
        #                 "Sharpe",
        #                 # "Prob. Sharpe Ratio",
        #                 "MTD",
        #                 "3M",
        #                 "6M",
        #                 "YTD",
        #                 "1Y",
        #                 "Max Drawdown",
        #                 # "Longest DD Days",
        #                 "Avg. Drawdown",
        #                 # "Avg. Drawdown Days",
        #             ]
        #         ]
        #     )
        # )
        # st.dataframe(
        #     met.loc[
        #         [
        #             "Longest DD Days",
        #             "Avg. Drawdown Days",
        #         ]
        #     ]
        # )

        # _ = pd.concat(
        #     [
        #         (dfr + 1).cumprod() - 1,
        #         # mff.max_draw_down(df),
        #         moving_window_df(dfr, window, _f),
        #     ],
        #     axis=1,
        # )

        d = (dfr + 1).cumprod()
        st.write(d.name.replace("_", " "))
        d.name = code
        st.line_chart(d - 1, height=h)

        # d = mff.max_draw_down(df_)
        d = d / d.rolling(len(d), min_periods=1).max() - 1
        st.write("max draw down")
        d.name = code
        st.area_chart(d, height=h)

        _ = df_.asfreq("D").ffill().asfreq("M").pct_change().dropna()
        if len(_) > 0:
            _.name = code
            st.write("monthly return")
            st.bar_chart(_, height=h)

        st.write("histgram(daily return%)")
        count, division = np.histogram(dfr, bins=20)
        st.bar_chart(
            pd.Series(count, np.round(division[1:] * 100, 1), name=code), height=h
        )

        _ = moving_window_df(dfr, window, _f)
        if _ is not None:
            for c, d in _.items():
                st.write(c.replace("_", " ") + " ({}days)".format(window))
                d.name = code
                st.line_chart(d, height=h)

        # st.pyplot(qs.plots.monthly_heatmap(dfr, square=True, show=False))

        # st.write("histgram(monthly return)")
        # count, division = np.histogram(_, bins=10)
        # st.bar_chart(
        #     pd.Series(count, np.round(division[1:] * 100, 1), name=""), height=h
        # )

        # st.dataframe(format_df(_.dropna()), height=200)

        # st.markdown("### Predict")
        # pred = predict_darts(dfr.asfreq("B", method="ffill"), n_pred=n_pred)

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

        # full report
        st.markdown("### Quantstats")
        f = df_.name
        bm = st.selectbox("select benchmark data", [None] + list(df.columns.drop(code)))
        if bm is not None:
            df_bm = df[bm]
            f += "_" + bm
            # df_ = pd.concat([df_, df_bm.loc[d1:d2]], axis=1)
        else:
            df_bm = None

        with st.spinner("Creating Full Analysis..."):
            filename_html = "quantstats_{}.html".format(f)
            st.download_button(
                "Download Quantstats Full Analysis",
                data=qs_html(df_, filename_html, benchmark=df_bm),
                file_name=filename_html,
            )

        st.markdown(
            "Generated by [QuantStats](https://github.com/ranaroussi/quantstats)",
            unsafe_allow_html=True,
        )


df = get_indices()
# df = load_csv()
if df is None:
    sample = """date	A	B
    2020-01-01	100	100
    2020-01-02	105	95
    2020-01-03	108	105
    2020-01-04	105	110
    2020-01-05	110	105
    2020-01-06	120	100
    2020-01-07	110	95
    2020-01-08	100	90
    """
    t = st.text_area("like csv", sample, placeholder=sample)
    df = pd.read_csv(
        io.StringIO(t.strip()), sep=None, index_col=0, parse_dates=True, engine="python"
    )
    st.write(format_df(df))

# df = pd.read_csv(sys.argv[1], index_col=0,
#                      parse_dates=True, usecols=[0, 1])

tsa_render(df)

# %%
