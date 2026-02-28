# Streamlit ダッシュボード構成

このリポジトリは、複数ページで機能を拡張できる Streamlit ダッシュボードの土台です。

## ディレクトリ構成

```text
.
├── app.py                # トップページ（インデックス）
├── pages/
│   ├── 01_Overview.py    # サマリ表示の例
│   ├── 02_Data_Explorer.py
│   └── 03_Settings.py
└── docs/
    └── streamlit-structure.md
```

## 拡張方法

1. `pages/` 配下に `NN_Page_Name.py` の形式で新しいページを追加。
2. 各ページで `st.title` と機能UIを実装。
3. `app.py` のトップページでは `pages/` 配下のファイルを自動で一覧表示。

## 実行方法

```bash
pip install streamlit pandas
streamlit run app.py
```
