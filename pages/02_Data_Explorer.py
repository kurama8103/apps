"""Data Explorer with PCA analysis from CSV upload or pasted data."""

from __future__ import annotations

from io import StringIO

import altair as alt
import pandas as pd
import streamlit as st
from sklearn.decomposition import PCA
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

st.title("Data Explorer / PCA")
st.write("CSVアップロードまたはクリップボードから貼り付けたデータを使ってPCAを実行します。")

upload = st.file_uploader("CSVファイルをアップロード", type=["csv"])
pasted_text = st.text_area(
    "またはCSVデータを貼り付け（クリップボードの内容をそのまま貼り付け可能）",
    height=180,
    placeholder="col1,col2,col3\n1,2,3\n4,5,6",
)

source_df: pd.DataFrame | None = None

if upload is not None:
    source_df = pd.read_csv(upload)
elif pasted_text.strip():
    source_df = pd.read_csv(StringIO(pasted_text.strip()))

if source_df is None:
    st.info("まずはCSVをアップロードするか、CSV文字列を貼り付けてください。")
    st.stop()

st.subheader("Raw Data")
st.dataframe(source_df, use_container_width=True)

numeric_df = source_df.select_dtypes(include=["number"]).copy()
if numeric_df.shape[1] < 2:
    st.warning("PCAには2列以上の数値カラムが必要です。")
    st.stop()

st.subheader("PCA 設定")
max_components = min(numeric_df.shape[1], numeric_df.shape[0])
if max_components < 2:
    st.warning("PCAには2行以上かつ2列以上の数値データが必要です。")
    st.stop()
n_components = st.slider("主成分数", min_value=2, max_value=max_components, value=2)

imputer = SimpleImputer(strategy="mean")
scaled_values = StandardScaler().fit_transform(imputer.fit_transform(numeric_df))

pca = PCA(n_components=n_components)
pca_result = pca.fit_transform(scaled_values)

pca_df = pd.DataFrame(
    pca_result,
    columns=[f"PC{i + 1}" for i in range(n_components)],
)

st.subheader("Explained Variance")
variance_df = pd.DataFrame(
    {
        "component": [f"PC{i + 1}" for i in range(n_components)],
        "ratio": pca.explained_variance_ratio_,
    }
)
st.dataframe(variance_df, use_container_width=True)

bar_chart = (
    alt.Chart(variance_df)
    .mark_bar()
    .encode(x="component:N", y=alt.Y("ratio:Q", title="Explained Variance Ratio"))
    .properties(height=300)
)
st.altair_chart(bar_chart, use_container_width=True)

st.subheader("PCA Scatter (PC1 vs PC2)")
color_column = st.selectbox(
    "色分けに使うカラム（任意）",
    options=["なし"] + list(source_df.columns),
)

plot_df = pca_df.copy()
plot_df["row"] = plot_df.index.astype(str)
if color_column != "なし":
    plot_df[color_column] = source_df[color_column].astype(str)

scatter = alt.Chart(plot_df).mark_circle(size=80).encode(
    x=alt.X("PC1:Q", title="PC1"),
    y=alt.Y("PC2:Q", title="PC2"),
    tooltip=list(plot_df.columns),
    color=alt.Color(f"{color_column}:N") if color_column != "なし" else alt.value("#1f77b4"),
).interactive()

st.altair_chart(scatter, use_container_width=True)

st.subheader("PCA Output")
st.dataframe(pca_df, use_container_width=True)
