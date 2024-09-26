from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, expected_returns, plotting
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from st_util import load_csv, format_df

plt.rcParams["figure.figsize"] = 8, 4

# import japanize_matplotlib
# japanize_matplotlib.japanize()


def pf_opt(return_index):
    ef = EfficientFrontier(
        expected_returns.mean_historical_return(return_index),
        risk_models.sample_cov(return_index),
    )
    ef.min_volatility()
    _r, _v, _sr = ef.portfolio_performance()
    res_opt = {
        "min_volatility": {
            "weight": ef.weights.tolist(),
            "Expected annual return": _r,
            "annual volatility": _v,
            "Sharpe Ratio": _sr,
        }
    }
    fig, ax = plt.subplots()
    ax.scatter(_v, _r, marker="x", s=50, c="b", label="Minimum Vol")

    ef = EfficientFrontier(
        expected_returns.mean_historical_return(return_index),
        risk_models.sample_cov(return_index),
    )
    ef.max_sharpe()
    _r, _v, _sr = ef.portfolio_performance()
    res_opt_ = {
        "max_sharpe": {
            "weight": ef.weights.tolist(),
            "Expected annual return": _r,
            "annual volatility": _v,
            "Sharpe Ratio": _sr,
        }
    }
    res_opt.update(res_opt_)
    ax.scatter(_v, _r, marker="*", s=100, c="r", label="Max Sharpe")

    ef = EfficientFrontier(
        expected_returns.mean_historical_return(return_index),
        risk_models.sample_cov(return_index),
        weight_bounds=(-1, 1),
    )
    ef.max_sharpe()
    _r, _v, _sr = ef.portfolio_performance()
    res_opt_ = {
        "max_sharpe_short": {
            "weight": ef.weights.tolist(),
            "Expected annual return": _r,
            "annual volatility": _v,
            "Sharpe Ratio": _sr,
        }
    }
    res_opt.update(res_opt_)
    ax.scatter(_v, _r, marker="+", s=50, c="g", label="Max Sharpe (Short)")

    ef = EfficientFrontier(
        expected_returns.mean_historical_return(return_index),
        risk_models.sample_cov(return_index),
    )
    plotting.plot_efficient_frontier(
        ef, ax=ax, weight_bounds=(None, None), show_assets=True, show_tickers=True
    )

    return res_opt, plt


def main():
    df_ = load_csv()
    if df_ is not None:
        # st.markdown("return, volatility and sharpe ratio")
        # df_assets = pd.DataFrame(
        #     {
        #         "Expected annual return": expected_returns.mean_historical_return(df_),
        #         "annual volatility": (
        #             expected_returns.returns_from_prices(df_).var() * 252
        #         )
        #         ** 0.5,
        #     }
        # )
        # df_assets["Sharpe Ratio"] = df_assets.iloc[:, 0] / df_assets.iloc[:, 1]
        # st.bar_chart(format_df(pd.DataFrame(df_assets).T),
        #              stack=False,
        #              horizontal=True)

        st.markdown("Optimazed portfolio weights")
        res_opt, plt = pf_opt(df_)
        st.bar_chart(
            pd.DataFrame(
                {k: v["weight"] for k, v in res_opt.items()}, index=df_.columns
            ).T.round(2),
            height=200,
            horizontal=True,
        )

        st.markdown("return, volatility and sharpe ratio")
        st.bar_chart(
            format_df(pd.DataFrame(res_opt).drop("weight")),
            stack=False,
            horizontal=True,
        )
        st.markdown("efficient frontier")
        st.pyplot(plt)
        # st.json(res_opt,expanded=False)


main()
