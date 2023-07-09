# -*- coding: utf-8 -*-

import quantstats as qs
import pandas as pd
import numpy as np
import streamlit as st


def load_csv():
    s = 'Choose a CSV file. '
    s += 'The first column of the file is the date, the first row is the column name.'

    uploaded_file = st.file_uploader(s, type='csv',)
    if uploaded_file is None:
        if 'df' in st.session_state:
            return st.session_state['df']
    else:
        df = pd.read_csv(uploaded_file, index_col=0,
                         parse_dates=True, usecols=[0, 1])
        st.session_state['df'] = df
        return df


def format_df(df):
    df = df.round(4)
    df.index = df.index.astype(str)
    return df


def tsa_render():
    qs.extend_pandas()
    n_pred = 10
    df_ = load_csv()
    if df_ is not None:
        df = df_[st.selectbox('select data', df_.columns)]
        if min(df) < 0:
            pass
        else:
            dfr = df.pct_change().dropna()

        st.markdown('### Input data')
        st.text(
            'From '+df.index[0].strftime('%Y-%m-%d')+' To '+df.index[-1].strftime('%Y-%m-%d')+'\n' +
            str((df.index[-1]-df.index[0]).days)+' days (' +
            str(round((df.index[-1]-df.index[0]).days/365, 2))+' years)'
        )

        st.line_chart(df, height=200)

        col1, col2 = st.columns(2)
        with col1:
            l = ['cagr', 'volatility', 'sharpe', 'max_drawdown', 'skew', 'kurtosis',
                 'kelly_criterion', 'value_at_risk', 'expected_shortfall']
            d = {'Cumulative Return': (df[-1]/df[0]).round(4)}
            for s in l:
                t = eval('df.{}()'.format(s))
                d.update({s: t})
            st.dataframe(pd.Series(d, name='Value'))
        with col2:
            st.dataframe(format_df(df))

        st.markdown('### Predict')
        pred = predict_darts(dfr.asfreq('B'), n_pred=n_pred)

        import statsmodels.api as sm

        models = {
            'UnobservedComponents': sm.tsa.UnobservedComponents(dfr, 'local linear trend', cycle=True),
            'SARIMAX': sm.tsa.SARIMAX(dfr, order=(5, 1, 5))
        }
        for k, v in models.items():
            res = v.fit()
            pred[k] = res.forecast(n_pred)

        pred['mean'] = pred.mean(axis=1)
        pred = pd.concat([dfr.tail(20), pred], axis=1)

        if st.checkbox('cumulative'):
            d_ = (pred+1).cumprod()
            d_.iloc[:, 0] = d_.iloc[:, 0]/(d_.iloc[:, 0].dropna()[-1])
        else:
            d_ = pred
        st.line_chart(d_, height=200)
        st.dataframe(format_df(d_))

        # full report
        st.markdown('### Quantstats')
        with st.spinner('Creating Full Analysis...'):
            filename_html = 'quantstats_'+df.name+'.html'
            st.download_button(
                'Download Quantstats Full Analysis',
                data=qs_html(df, filename_html),
                file_name=filename_html)

        st.markdown(
            'Generated by [QuantStats](https://github.com/ranaroussi/quantstats)',
            unsafe_allow_html=True)

        st.markdown('### pyfolio')     
        import pyfolio as pf
        # import matplotlib.pyplot as plt
        # fig,ax=plt.subplots()
        # ax=pf.plotting.plot_drawdown_underwater(returns=dfr,ax=ax)
        # st.pyplot(fig)
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot(pf.tears.create_simple_tear_sheet(returns=dfr))


@st.cache(show_spinner=False)
def qs_html(df: pd.DataFrame, download_filename):
    qs.reports.html(df, rf=0., title=df.name,
                    download_filename=download_filename,
                    output='./tmp/')

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
        ExponentialSmoothing(),
        Prophet(),
        RandomForest(lags=5),
        RegressionModel(lags=5),
    ]

    pred = pd.DataFrame()
    for model in models:
        p_ = model.fit(series=train).predict(n_pred).pd_series()
        s = str(model)
        if s.find('(') > 0:
            s = s[:s.find('(')]
        p_.name = s
        pred = pd.concat([pred, p_], axis=1)
    pred.index = pd.to_datetime(pred.index)
    return pred


def mape(pred, true):
    return np.mean(np.abs((pred - true) / true))*100


tsa_render()
