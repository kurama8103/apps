import streamlit as st
import pandas as pd
from pypfopt import black_litterman, risk_models, expected_returns
from pypfopt.efficient_frontier import EfficientFrontier
from src.st_util import load_csv
import matplotlib.pyplot as plt
import japanize_matplotlib

japanize_matplotlib.japanize()

def main():
    st.title("Black-litterman Portfolio Optimization")

    df_ = load_csv()

    if df_ is not None:
        if "Date" in df_.columns:
            df = df_.set_index("Date")
        else:
            df = df_
        st.subheader("Investor Views (Absolute)")

        # Create a dictionary to store the views
        views = {}

        # Create a number input for each asset
        for col in df.columns:
            views[col] = st.number_input(f"View for {col}", value=0.0, step=0.01)

        # Display the views for confirmation
        st.write("Current Views:")
        st.write(views)

        st.subheader("Market Caps")
        market_caps = {}
        for col in df.columns:
            market_caps[col] = st.number_input(f"Market Cap for {col}", value=1e9, step=1e6)

        st.write("Current Market Caps:")
        st.write(market_caps)

        market_proxy = st.selectbox("Select Market Proxy", df.columns)

        if st.button("Run Black-Litterman Optimization"):
            # Calculate expected returns and sample covariance
            S = risk_models.sample_cov(df)

            # Calculate market-implied prior returns
            delta = black_litterman.market_implied_risk_aversion(df[market_proxy])
            prior = black_litterman.market_implied_prior_returns(market_caps, delta, S)

            # Create BlackLittermanModel
            # Filter out views that are 0.0, as they are not really "views"
            views_filtered = {k: v for k, v in views.items() if v != 0.0}
            bl = black_litterman.BlackLittermanModel(S, pi=prior, absolute_views=views_filtered)

            # Calculate posterior returns
            posterior_rets = bl.bl_returns()

            st.subheader("Posterior Expected Returns")
            st.write(posterior_rets)

            # Optimize portfolio
            ef = EfficientFrontier(posterior_rets, S)
            ef.max_sharpe()
            weights = ef.clean_weights()

            st.subheader("Optimized Portfolio Weights")
            st.bar_chart(pd.Series(weights))

            st.subheader("Optimized Portfolio Performance")
            expected_return, volatility, sharpe_ratio = ef.portfolio_performance()
            st.write(f"Expected annual return: {expected_return:.2%}")
            st.write(f"Annual volatility: {volatility:.2%}")
            st.write(f"Sharpe Ratio: {sharpe_ratio:.2f}")

if __name__ == "__main__":
    main()
