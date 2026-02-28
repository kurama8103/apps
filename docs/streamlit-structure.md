# Streamlit ダッシュボード構成

このリポジトリは、複数ページで機能を拡張できる Streamlit ダッシュボードの土台です。

## ディレクトリ構成

```text
.
├── app.py                # トップページ（インデックス）
├── pages/
│   ├── 01_Overview.py    # サマリ表示の例
│   ├── 02_Data_Explorer.py # CSV入力とPCA分析
│   └── 03_Settings.py
└── docs/
    └── streamlit-structure.md
```

## 拡張方法

1. `pages/` 配下に `NN_Page_Name.py` の形式で新しいページを追加。
2. 各ページで `st.title` と機能UIを実装。
3. `app.py` のトップページでは `pages/` 配下のファイルを自動で一覧表示。

## Data Explorer/PCA ページ仕様

- 入力方法
  - CSVファイルのアップロード
  - クリップボードの内容をCSVとしてテキストエリアに貼り付け
- 処理
  - 数値カラムを自動抽出
  - 欠損値は平均値補完
  - 標準化後に `sklearn.decomposition.PCA` で次元圧縮
- 出力
  - 寄与率テーブルと棒グラフ
  - PC1/PC2 散布図（任意カラムで色分け）
  - 主成分スコアテーブル

## 実行方法

```bash
pip install -r requirements.txt
streamlit run app.py
```
