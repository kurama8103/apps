from src.st_util import load_csv, class_to_csv, flg_use_pct, multiselect_X_y
import streamlit as st
import pandas as pd

from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = 8, 4
pd.options.plotting.backend = "matplotlib"


def main():
    df_ = load_csv().dropna()
    if df_ is not None:
        df_, flg_pct = flg_use_pct(df_, True)
        X, y = multiselect_X_y(df_)
        if X.shape[1] > 1:
            res2d=df_
            col=df_.columns
            if X.shape[1]>2:
                st.info("Dimensionality reduction by PCA")
                res2d = PCA(n_components=2).fit_transform(X, y)
                col=["PC1", "PC2"]
            cls = KMeans(2)
            cls.fit(res2d)

            df = pd.DataFrame(res2d, columns=col).assign(color=cls.labels_)
            st.scatter_chart(df, x=col[0], y=col[1], color="color")

            st.json(cls.__dict__)
            st.download_button("CSV file", class_to_csv(cls).getvalue(), mime="text/csv")


main()
