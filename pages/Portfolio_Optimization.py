import re
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, expected_returns, plotting
import matplotlib.pyplot as plt

import pandas as pd
import streamlit as st

import seaborn as sns
sns.set_style('whitegrid')

import japanize_matplotlib
japanize_matplotlib.japanize()


def load_csv():
    s = 'Choose a CSV file. '
    s += 'The first column of the file is the date, the first row is the column name.'

    uploaded_file = st.file_uploader(s, type='csv',)
    if uploaded_file is None:
        if 'df' in st.session_state:
            return st.session_state['df']
    else:
        df = pd.read_csv(uploaded_file, index_col=0,
                         parse_dates=True)
        st.session_state['df'] = df
        return df


def pf_opt(return_index):
    ef = EfficientFrontier(
        expected_returns.mean_historical_return(return_index),
        risk_models.sample_cov(return_index))
    ef.min_volatility()
    _r, _v, _sr = ef.portfolio_performance()
    res_opt = {
        'min_volatility': {
            'weight': ef.weights.tolist(),
            'Expected annual return': _r,
            'annual volatility': _v,
            'Sharpe Ratio': _sr
        }}
    fig, ax = plt.subplots()
    ax.scatter(_v, _r, marker="x", s=50, c="b", label="Minimum Vol")

    ef = EfficientFrontier(
        expected_returns.mean_historical_return(return_index),
        risk_models.sample_cov(return_index))
    ef.max_sharpe()
    _r, _v, _sr = ef.portfolio_performance()
    res_opt_ = {
        'max_sharpe': {
            'weight': ef.weights.tolist(),
            'Expected annual return': _r,
            'annual volatility': _v,
            'Sharpe Ratio': _sr
        }}
    res_opt.update(res_opt_)
    ax.scatter(_v, _r, marker="*", s=100, c="r", label="Max Sharpe")

    ef = EfficientFrontier(
        expected_returns.mean_historical_return(return_index),
        risk_models.sample_cov(return_index),
        weight_bounds=(-1, 1))
    ef.max_sharpe()
    _r, _v, _sr = ef.portfolio_performance()
    res_opt_ = {
        'max_sharpe_short': {
            'weight': ef.weights.tolist(),
            'Expected annual return': _r,
            'annual volatility': _v,
            'Sharpe Ratio': _sr
        }}
    res_opt.update(res_opt_)
    ax.scatter(_v, _r, marker="+", s=50, c="g", label="Max Sharpe (Short)")

    ef = EfficientFrontier(
        expected_returns.mean_historical_return(return_index),
        risk_models.sample_cov(return_index))
    plotting.plot_efficient_frontier(
        ef,
        ax=ax,
        weight_bounds=(None, None),
        show_assets=True,
        show_tickers=True
    )

    return res_opt, plt


def format_df(df):
    df = df.round(4)
    df.index = df.index.astype(str)
    return df


def render_pf_opt():
    df = load_csv()
    if df is not None:
        st.dataframe(format_df(df), height=200)
        st.text('assets')
        df_assets = pd.DataFrame({
            'Expected annual return': expected_returns.mean_historical_return(df),
            'annual volatility': (expected_returns.returns_from_prices(df).var()*252)**0.5,
        })
        df_assets['Sharpe Ratio'] = df_assets.iloc[:, 0]/df_assets.iloc[:, 1]
        st.dataframe(pd.DataFrame(df_assets))

        st.text('Optimaze portfolio')
        res_opt, plt = pf_opt(df)
        st.dataframe(pd.DataFrame(res_opt).drop('weight').T)

        st.text('efficient frontier')
        st.pyplot(plt)

        st.text('weight')
        for k, v in res_opt.items():
            st.write(k)
            st.bar_chart(pd.DataFrame(v['weight'], df.columns), width=50,)
        
        st.json(res_opt)

render_pf_opt()
