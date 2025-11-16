from st_util import load_csv, class_to_csv, flg_use_pct, multiselect_X_y
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from yellowbrick.features import pca_decomposition
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = 8, 4
pd.options.plotting.backend = "matplotlib"


def main():
    h = 200
    df_ = load_csv()
    if df_ is not None:
        # flg_pct = st.session_state["flg_pct"]
        df_, flg_pct = flg_use_pct(df_, True)
        # target = st.selectbox("select target", df_.columns)
        # features = st.multiselect(
        #     "select features",
        #     list(df_.columns.drop(target)),
        #     default=list(df_.columns.drop(target)),
        # )

        # y = df_[target]
        # X = df_[features]
        X, y = multiselect_X_y(df_)
        if X.shape[1] > 1:
            st.markdown("features component plot")
            fig, ax = plt.subplots()
            res = pca_decomposition(
                X, y, scale=True, proj_features=True, show=False, ax=ax
            )
            st.pyplot(fig)

            cls = PCA(n_components=2)
            res = cls.fit_transform(X, y)
            if flg_pct:
                res = np.cumprod(res + 1, axis=0) - 1

            col = ["PC1", "PC2"]
            st.text("factor return")
            st.line_chart(pd.DataFrame(res, y.index, columns=col), height=h)
            st.text("factor exposure")
            st.bar_chart(
                pd.DataFrame(cls.components_.T, index=X.columns, columns=col),
                stack=False,
                height=h,
            )

            st.json(cls.__dict__)
            st.download_button("CSV file", class_to_csv(cls).getvalue(), mime="text/csv")


main()
