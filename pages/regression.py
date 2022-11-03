from multiprocessing.resource_sharer import stop
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge, Lasso,LassoCV
#from Time_Series_Analysis import load_csv
import streamlit as st

def summary_model_sk(model,x,y):
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

def load_csv_s():
    s = 'CSVファイルは1列目を日付、2列目をデータとして認識し、他の列は無視されます。\n'
    s += '1行目は列名として認識されます。日本語名でも動作はしますが文字化けします。'
    st.text(s)

    uploaded_file = st.file_uploader("Choose a CSV file", type='csv',)
    if uploaded_file is None:    
        if 'df' in st.session_state:
            return st.session_state['df']
    else:
        df = pd.read_csv(uploaded_file, index_col=0,
                        parse_dates=True)
        st.session_state['df'] = df
        return df


df=load_csv_s()
if df is not None:
    df_=df
    if st.checkbox('price 1'):
        df_=df_/df_.iloc[0]
    
    flg=0
    if st.checkbox('pct_change'):
        df_=df_.pct_change().dropna()
        flg=1

    st.line_chart(df_,height=200)
    st.write(df_)
    y=st.selectbox('Y',df_.columns)
    c=list(df_.columns.drop(y))
    x=st.multiselect('X',c,c)
    if len(x)==0:
        st.stop()

    model = LinearRegression(fit_intercept=True, normalize=False)
    res=summary_model_sk(model,df_[x],df_[y])
    st.write(model,res['score'])
    st.json(res,expanded=False)

    model = LassoCV(fit_intercept=True, normalize=False,alphas=[0,0.01,0.1,1,10],cv=5)
    res=summary_model_sk(model,df_[x],df_[y])
    st.write(model,res['score'])
    st.json(res,expanded=False)

    pred=(df_[x]*res['coef']).sum(axis=1)+res['intercept']
    pred.name='prediction'
    pred=pd.concat([pred,df_[y]],axis=1)
    if flg==1:
        pred=(1+pred).cumprod()
    st.line_chart(pred,height=200)

    
pass