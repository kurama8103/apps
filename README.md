# Streamlit Dashboard App

Streamlit を使ったマルチページダッシュボードの基本構成です。

## セットアップ

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 起動

```bash
streamlit run app.py
```

## 主なページ

- `app.py`: トップページ（全体インデックス）
- `pages/01_Overview.py`: KPIサマリ例
- `pages/02_Data_Explorer.py`: CSVアップロード / クリップボード貼り付け / sklearn toy data 入力 + PCA分析
- `pages/03_Settings.py`: 設定フォームの雛形

## 構成ドキュメント

- `docs/streamlit-structure.md`
