# -*- coding: utf-8 -*-

import streamlit as st
from st_util import load_csv, load_test_data, get_indices

# import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = 8, 8

st.set_page_config(layout="wide")

st.title("TOP Page")
st.write(
    """
    time series plots: \n
    simulation portfolio: \n
    machine learning analysis: \n
    """
)
# if st.checkbox("Use Sample Data"):
# st.header("US Macroeconomic Data from FRED")
# st.json({
#     "realgdp": "Real gross domestic product",
#     "realcons": "Real personal consumption expenditures",
#     "realinv" :"Real gross private domestic investment",
#     "realgovt":"Real federal consumption expenditures & gross investment",
#     "realdpi": "Real private disposable income",
#     "cpi" :"Consumer price index",
#     "m1": "M1 nominal money stock",
#     "tbilrate": "3-monthtreasury bill",
#     "unemp" :"Unemployment rate",
#     "pop":"Population",
#     "infl":"Inflation rate (cpi base)",
#     "realint":"Real interest rate (tbilrate - infl)"
#     })
# df = pd.concat([load_test_data()[1], load_test_data()[0]], axis=1)
#     st.header("Currency Data (USDJPY and USDEUR) from FRED")
#     df = get_indices(False)
#     st.session_state["df"] = df
# else:
#     st.session_state["df"] = None
st.markdown("### data outlook")
df = load_csv()

if df is not None:
    st.dataframe(
        df.style.set_properties(
            **{"background-color": "lightyellow"}, subset=df.columns[0]
        )
    )
    st.write("Pairplot first 5 columns")
    st.pyplot(sns.pairplot(data=df.iloc[:, :5]))
    st.write("Clustermap of correlation")
    st.pyplot(
        sns.clustermap(
            df.corr().round(2), row_cluster=True, annot=True, center=0, figsize=(6, 6)
        )
    )
