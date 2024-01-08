import japanize_matplotlib
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, expected_returns, plotting
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Ridge, Lasso, LassoCV

import pandas as pd
import streamlit as st
from st_util import load_csv

import seaborn as sns
sns.set_style('whitegrid')

japanize_matplotlib.japanize()


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
    df_ = load_csv()
    if df_ is not None:
        st.text('graph')
        flg = show_graphs(df_)

        st.text('Return of assets')
        show_returns(df_)

        # calc_regression(df_, flg)

        st.text('mean and volatility')
        df_assets = pd.DataFrame({
            'Expected annual return': expected_returns.mean_historical_return(df_),
            'annual volatility': (expected_returns.returns_from_prices(df_).var()*252)**0.5,
        })
        df_assets['Sharpe Ratio'] = df_assets.iloc[:, 0]/df_assets.iloc[:, 1]
        st.dataframe(pd.DataFrame(df_assets))

        st.text('Optimaze portfolio')
        res_opt, plt = pf_opt(df_)
        st.dataframe(pd.DataFrame(res_opt).drop('weight').T)

        st.text('efficient frontier')
        st.pyplot(plt)

        st.text('weight')
        for k, v in res_opt.items():
            st.write(k)
            st.bar_chart(pd.DataFrame(v['weight'], df_.columns), width=50,)

        st.json(res_opt)


def show_returns(df_):
    fig, ax = plt.subplots()
    _ = df_.iloc[-1]/df_.iloc[[-2, -4, -7, -13]]-1
    _.index = ['1M', '3M', '6M', '12M']
    sns.heatmap(_.T, center=0,
                annot=True, fmt='.1%', cmap='PiYG')
    st.write(fig)


def show_graphs(df_):
    if st.checkbox('price 1'):
        df_ = df_/df_.iloc[0]

    flg = 0
    if st.checkbox('pct_change'):
        df_ = df_.pct_change().dropna()
        flg = 1

    st.line_chart(df_, height=200)
    st.write(format_df(df_))
    return flg


def calc_regression(df_, flg=0):
    y = st.selectbox('Y', df_.columns)
    c = list(df_.columns.drop(y))
    x = st.multiselect('X', c, c)
    if len(x) == 0:
        st.stop()

    model = LinearRegression(fit_intercept=True, normalize=False)
    res = summary_model_sk(model, df_[x], df_[y])
    st.write(model, res['score'])
    st.json(res, expanded=False)

    model = LassoCV(fit_intercept=True, normalize=False,
                    alphas=[0, 0.01, 0.1, 1, 10], cv=5)
    res = summary_model_sk(model, df_[x], df_[y])
    st.write(model, res['score'])
    st.json(res, expanded=False)

    pred = (df_[x]*res['coef']).sum(axis=1)+res['intercept']
    pred.name = 'prediction'
    pred = pd.concat([pred, df_[y]], axis=1)
    if flg == 1:
        pred = (1+pred).cumprod()
    st.line_chart(pred, height=200)


def summary_model_sk(model, x, y):
    model.fit(x, y)
    res = {
        #        'model': model,
        'score': model.score(x, y),
        'intercept': model.intercept_,
        'coef': model.coef_.tolist(),
        #        'predict':model.predict(x),
        'params': model.get_params()
    }
    return res


render_pf_opt()