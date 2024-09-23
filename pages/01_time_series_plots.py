# %%
# -*- coding: utf-8 -*-

import quantstats as qs
import pandas as pd
import numpy as np
import streamlit as st
from st_util import (
    load_csv,
    get_indices,
    format_df,
    moving_window_df,
)

pd.options.plotting.backend = "matplotlib"


# @st.cache_resource(show_spinner=False)
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
        output="tmp/" + download_filename,
        benchmark=benchmark,
    )

    with open("tmp/" + download_filename) as f:
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
        # "momentum": momentum(x),
        # "cvar": mff.cvar(x)[1],
        # "adf":mff.adf_summary(x)['adf'],
        # "max_draw_down": np.cumprod(x + 1)[-1] / np.cumprod(x + 1).max() - 1,
    }
    return d


def tsa_render(df):
    h = 200
    window = 180
    color_set = ["#4BA5FF", "#9eacac"]

    qs.extend_pandas()

    st.markdown("### Time series plots")
    if df is None:
        df = get_indices().dropna()
        st.write("## test data (currency)")

    if df is not None:
        code = st.selectbox("select data", df.columns)
        bm = st.selectbox("select benchmark data", [None] + list(df.columns.drop(code)))

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
        df_ = df.filter(items=[code, bm]).loc[d1:d2].ffill().dropna()
        dfr = df_.pct_change().fillna(0)
        dfr.name = "cumulative_return"

        if bm:
            if df.columns.get_loc(code) > df.columns.get_loc(bm):
                color = color_set
            else:
                color = color_set[::-1]
        else:
            color = [color_set[0]]
        st.text(
            ""
            + str((df_.index[-1] - df_.index[0]).days)
            + " days ("
            + str(round((df_.index[-1] - df_.index[0]).days / 365, 2))
            + " years)"
        )

        st.write(code)
        # st.line_chart((df_[code]), height=h, color=color_set[0])
        st.line_chart(format_df(df_[code]), height=h)

        if bm:
            st.write(bm)
            st.line_chart(
                format_df(df_[bm]),
                height=h,
                #   color=color_set[-1]
            )

        st.write("cumulative return")
        d = (dfr + 1).cumprod()
        d.name = code
        st.area_chart(format_df(d - 1), height=h, stack=False)
        #   color=color,

        st.write("draw down")
        d = d / d.rolling(len(d), min_periods=1).max() - 1
        d.name = code
        st.area_chart(
            format_df(d),
            height=h,
            #   color=color,
            stack=False,
        )

        _ = dfr.asfreq("BM")
        if len(_) > 0:
            st.write("monthly return")
            _.name = code
            st.bar_chart(
                format_df(_),
                height=h,
                #  color=color,
                stack=False,
            )

        st.write("histgram (daily return, %)")
        if bm:
            count, division = np.histogram(dfr, bins=20)
            h1 = np.histogram(dfr[code], bins=20, range=(division[0], division[-1]))[0]
            h2 = np.histogram(dfr[bm], bins=20, range=(division[0], division[-1]))[0]
            hg = pd.DataFrame({code: h1, bm: h2}, np.round(division[1:] * 100, 1))
            st.bar_chart(
                hg,
                height=h,
                #  color=color,
                stack=False,
            )
        else:
            count, division = np.histogram(dfr[code], bins=20)
            hg = pd.Series(count, np.round(division[1:] * 100, 1))
            st.bar_chart(
                hg,
                height=h,
                #  color=color[-1]
            )

        st.markdown("### moving window metrics")
        _ = moving_window_df(dfr[code], window, _f)
        if bm:
            _bm = moving_window_df(dfr[bm], window, _f)
        if _ is not None:
            for c, d in _.items():
                st.write(c.replace("_", " ") + " (rolling {} days)".format(window))
                d.name = code
                if bm:
                    st.area_chart(
                        format_df(pd.DataFrame({code: d, bm: _bm[c]})),
                        height=h,
                        # color=color,
                        stack=False,
                    )
                else:
                    st.area_chart(
                        d,
                        height=h,
                        #   color=color,
                        stack=False,
                    )
            if bm:
                st.write("returns correlation (rolling {} days)".format(window))
                st.line_chart(
                    format_df(
                        moving_window_df(
                            dfr[[code, bm]], window, lambda x: np.corrcoef(x)[0, 1]
                        ),
                    ),
                    height=h,
                    # color=color_set[0],
                )

        # full report
        st.markdown("### Quantstats")
        f = code
        if bm is not None:
            df_bm = df_[bm]
            f += "_" + bm
        else:
            df_bm = None

        with st.spinner("Creating Full Analysis..."):
            filename_html = "quantstats_{}.html".format(f)
            s = qs_html(df_[code], download_filename=filename_html, benchmark=df_bm)
            st.download_button(
                "Download Quantstats Full Analysis",
                data=s,
                file_name=filename_html,
            )

        st.markdown(
            "Generated by [QuantStats](https://github.com/ranaroussi/quantstats)",
            unsafe_allow_html=True,
        )


df = load_csv()
if df is None:
    # sample = """date	A	B
    # 2020-01-01	100	100
    # 2020-01-02	105	95
    # 2020-01-03	108	105
    # 2020-01-04	105	110
    # 2020-01-05	110	105
    # 2020-01-06	120	100
    # 2020-01-07	110	95
    # 2020-01-08	100	90
    # """
    # t = st.text_area("like csv", sample, placeholder=sample)
    # df = pd.read_csv(
    #     io.StringIO(t.strip()), sep=None, index_col=0, parse_dates=True, engine="python"
    # )
    df = get_indices(False).dropna()
    st.write("## test data (currency)")
    # st.write(format_df(df))

tsa_render(df)
# %%
