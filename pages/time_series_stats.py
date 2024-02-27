# %%
# -*- coding: utf-8 -*-

import quantstats as qs
import pandas as pd
import numpy as np
import streamlit as st
import io
from st_util import (
    load_csv,
    get_indices,
    format_df,
    momentum,
    moving_window_df,
)

pd.options.plotting.backend = "matplotlib"
# import myfunc.finfunc as mff
# def mape(pred, true):
#     return np.mean(np.abs((pred - true) / true)) * 100


@st.cache(show_spinner=False)
def qs_html(
    df: pd.DataFrame,
    download_filename: str,
    benchmark: pd.DataFrame = None,
    rf: float = 0.0,
):
    qs.reports.html(
        df,
        rf=rf,
        title=df.name,
        download_filename=download_filename,
        output="./tmp/",
        benchmark=benchmark,
    )

    with open(download_filename) as f:
        s = f.read()

    return s


def _f(x):
    n = 252
    m = np.mean(x) * n
    s = np.std(x) * np.sqrt(n)
    d = {
        "cumlative_return": m,
        "standard_deviation": s,
        "sharpe_ratio": (m / s),
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

        d = (dfr + 1).cumprod()
        st.write(d.name.replace("_", " "))
        d.name = code
        st.line_chart(d - 1, height=h)

        st.write("max draw down")
        d = d / d.rolling(len(d), min_periods=1).max() - 1
        d.name = code
        st.area_chart(d, height=h)

        _ = df_.asfreq("D").ffill().asfreq("M").pct_change().dropna()
        if len(_) > 0:
            st.write("monthly return")
            _.name = code
            st.bar_chart(_, height=h)

        st.write("histgram(daily return%)")
        count, division = np.histogram(dfr, bins=20)
        st.bar_chart(
            pd.Series(count, np.round(division[1:] * 100, 1), name=code), height=h
        )

        _ = moving_window_df(dfr, window, _f)
        if _ is not None:
            for c, d in _.items():
                st.write(c.replace("_", " ") + " (rolling {}days)".format(window))
                d.name = code
                st.line_chart(d, height=h)

        # st.pyplot(qs.plots.monthly_heatmap(dfr, square=True, show=False))

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


tsa_render(df)

# %%
