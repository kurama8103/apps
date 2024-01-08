# -*- coding: utf-8 -*-

import pandas as pd
import streamlit as st
import sys


def load_csv():
    s = 'Choose a CSV file. '
    s += 'The first column of the file is the date, the first row is the column name.'

    uploaded_file = st.file_uploader(s, type='csv',)
    if uploaded_file is None:
        if 'df' in st.session_state:
            return st.session_state['df']
        else:
            print(sys.argv)
            # uploaded_file = sys.argv[1]
    else:
        df = pd.read_csv(uploaded_file, index_col=0, parse_dates=True)
        st.session_state['df'] = df
        return df
