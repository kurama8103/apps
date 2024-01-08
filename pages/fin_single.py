# %%
# -*- coding: utf-8 -*-

import quantstats as qs
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from st_util import load_csv


def format_df(df, digit=4):
    df = df.round(digit)
    df.index = df.index.astype(str)
    return df


def tsa_render(df_):
    qs.extend_pandas()
    n_pred = 10
    if df_ is not None:
        df = df_[st.selectbox("select data", df_.columns)]
        # bm = st.selectbox(
        #     "select benchmark data", [None] + list(df_.columns.drop(df.name))
        # )
        # if bm is not None:
        #     df_bm = df_[bm]
        # else:
        #     df_bm = None

        st.markdown("### Input data")
        df_ = df
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
        df_ = df.loc[d1:d2]

        if min(df_) < 0:
            pass
        else:
            dfr = df_.pct_change().dropna()
            dfr.name = "cum_ret"

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

        # st.line_chart(df, height=h)
        # st.line_chart(dfr.rolling(30).std() * np.sqrt(250), height=h)
        # st.line_chart(dfr.rolling(30).mean() / dfr.rolling(30).std(), height=h)

        # fig = plt.figure(figsize=(8, 2))
        # dfr.hist(bins=20)
        # st.pyplot(fig)

        # import plotly.express as px
        # st.plotly_chart(
        #     px.histogram(y=dfr, histnorm="probability density"),
        #     use_container_width=True,
        #     sharing="streamlit",
        #     theme="streamlit",
        # )

        # l = [
        #     "cagr",
        #     "volatility",
        #     "sharpe",
        #     "max_drawdown",
        #     "value_at_risk",
        #     "expected_shortfall",
        # ]
        # d = {"Cumulative Return": (df[-1] / df[0] - 1)}
        # for s in l:
        #     t = eval("df.{}()".format(s))
        #     d.update({s: t})
        # st.dataframe(pd.Series(d, name="Value"))

        # import myfunc.finfunc as mff
        from numpy.lib.stride_tricks import sliding_window_view
        import scipy

        def momentum(x, window=None):
            if window == None:
                window = len(x)
            r = np.cumprod(x[-window - 2 : -1] + 1)
            mom = r[-1] / r[0] - 1
            return x[-1] - mom

        def moving_window(x, window: int, func) -> list:
            return [func(d) for d in sliding_window_view(x, window)]

        def moving_window_df(x: pd.DataFrame, window: int, func) -> pd.DataFrame:
            return pd.DataFrame(
                moving_window(x.values, window, func),
                index=x.tail(len(x) + 1 - window).index,
            )

        def _f(x):
            n = 252
            m = np.mean(x) * n
            s = np.std(x) * np.sqrt(n)
            d = {
                "roll_ret": m,
                "std": s,
                "sharpe": (m / s),
                "skew": scipy.stats.skew(x),
                "kurt": scipy.stats.kurtosis(x),
                # "hurst": mff.hurst(x)[0],
                "mom": momentum(x),
                # "cvar": mff.cvar(x)[1],
                # "adf":mff.adf_summary(x)['adf'],
            }
            return d

        met = qs.reports.metrics(dfr, display=False)
        st.dataframe(
            met.loc[
                [
                    # "Start Period",
                    # "End Period",
                    "Risk-Free Rate",
                    "Cumulative Return",
                    "All-time (ann.)",
                    "CAGR﹪",
                    "Sharpe",
                    # "Prob. Sharpe Ratio",
                    "MTD",
                    "3M",
                    "6M",
                    "YTD",
                    "1Y",
                    "Max Drawdown",
                    "Longest DD Days",
                    "Avg. Drawdown",
                    "Avg. Drawdown Days",
                ]
            ].round(2)
        )

        _ = pd.concat(
            [
                (dfr + 1).cumprod(),
                # mff.max_draw_down(df),
                moving_window_df(dfr, 180, _f),
            ],
            axis=1,
        )
        h = 120
        for c, d in _.items():
            st.write(c)
            st.line_chart(d, height=h)

        # st.pyplot(qs.plots.monthly_heatmap(dfr, square=True, show=False))

        count, division = np.histogram(dfr, bins=20)
        st.bar_chart(
            pd.Series(count, np.round(division[1:] * 100, 1), name="histgram"), height=h
        )

        _ = df.asfreq("D").ffill().asfreq("M").pct_change().dropna()
        _.name = "month_ret"
        st.bar_chart(_, height=h)

        st.dataframe(format_df(_.dropna()), height=200)

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
        with st.spinner("Creating Full Analysis..."):
            filename_html = "quantstats_" + df.name + ".html"
            st.download_button(
                "Download Quantstats Full Analysis",
                data=qs_html(df_, filename_html, benchmark=None),
                file_name=filename_html,
            )

        st.markdown(
            "Generated by [QuantStats](https://github.com/ranaroussi/quantstats)",
            unsafe_allow_html=True,
        )


@st.cache(show_spinner=False)
def qs_html(df: pd.DataFrame, download_filename, benchmark=None):
    qs.reports.html(
        df,
        rf=0.0,
        title=df.name,
        download_filename=download_filename,
        output="./tmp/",
        benchmark=benchmark,
    )

    with open(download_filename) as f:
        s = f.read()

    return s


@st.cache(show_spinner=True, allow_output_mutation=True)
def predict_darts(series, n_pred=10, w=20):
    from darts.models import NaiveDrift, NaiveSeasonal, ExponentialSmoothing
    from darts.models import RandomForest, RegressionModel, AutoARIMA, Prophet
    from darts import TimeSeries

    train = TimeSeries.from_series(series)[-w:]

    models = [
        # NaiveDrift(n_pred),
        NaiveSeasonal(n_pred),
        AutoARIMA(),
        # ExponentialSmoothing(),
        # Prophet(),
        # RandomForest(lags=5),
        RegressionModel(lags=5),
    ]

    pred = pd.DataFrame()
    for model in models:
        p_ = model.fit(series=train).predict(n_pred).pd_series()
        s = str(model)
        if s.find("(") > 0:
            s = s[: s.find("(")]
        p_.name = s
        pred = pd.concat([pred, p_], axis=1)
    pred.index = pd.to_datetime(pred.index)
    return pred


def mape(pred, true):
    return np.mean(np.abs((pred - true) / true)) * 100


tsa_render(load_csv())


# # %%
# df = pd.read_csv(sys.argv[1], index_col=0,
#                      parse_dates=True, usecols=[0, 1])

# %%
