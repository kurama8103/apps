import matplotlib.pyplot as plt
import streamlit as st
from st_util import load_csv, format_df
import japanize_matplotlib

japanize_matplotlib.japanize()
plt.rcParams["figure.figsize"] = 8, 4
import pandas as pd


def main():
    df_ = load_csv()
    if df_ is not None:
        df_ = df_.dropna()
        flg_pct = False
        if st.checkbox("Use percentage change (return) data", True):
            df_ = df_.pct_change().dropna()
            flg_pct = True

        target = st.selectbox("select target", df_.columns)
        features = st.multiselect(
            "select features",
            list(df_.columns.drop(target)),
            default=list(df_.columns.drop(target)),
        )

        y = df_[target]
        X = df_[features]
        if X.shape[1] > 1:
            st.markdown("features component plot")
            res = vis_features(X, y)
            st.pyplot(res)

        st.markdown("model: LightGBM, score: R2")
        res = quick_regressor(X, y, True)
        st.text([(k,v.round(3)) for k,v in res[1]["r2"].items()])
        st.pyplot(res[1]["fig"])
        # st.json(res[1])

        w = len(df_) * 8 // 10
        h = 200
        st.markdown("Predict train data")
        pred = res[1]["model"].predict(X.head(w))
        _g = pd.DataFrame(y.head(w)).assign(predict=pred)
        if flg_pct:
            _g = (_g + 1).cumprod() - 1
        st.line_chart(_g, height=h)

        w = len(df_) - w
        st.markdown("Predict test data")
        pred = res[1]["model"].predict(X.tail(w))
        _g = pd.DataFrame(y.tail(w)).assign(predict=pred)
        if flg_pct:
            _g = (_g + 1).cumprod() - 1
        st.line_chart(_g, height=h)


def vis_features(X, y, figsize=(8, 4)):
    from yellowbrick.features import rank2d, pca_decomposition

    # from sklearn.cluster import KMeans
    # from yellowbrick.cluster.elbow import kelbow_visualizer

    fig, axes = plt.subplots(nrows=1, ncols=1, figsize=figsize)

    # rank2d(X, show=False, ax=axes[0])
    pca_decomposition(X, y, scale=True, proj_features=True, show=False, ax=axes)
    # f = kelbow_visualizer(KMeans(), X, k=(2, 10), show=False, ax=axes[2])
    return fig


def vis_model_regression(model, X_train, y_train, X_test, y_test, return_model=False):
    from yellowbrick.model_selection import feature_importances
    from yellowbrick.regressor import residuals_plot

    res = dict()
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(8, 5))
    _ = feature_importances(model, X_train, y_train, show=False, ax=axes[0])
    res["feat_imp"] = dict(zip(_.features_, _.feature_importances_))
    _ = residuals_plot(model, X_train, y_train, X_test, y_test, show=False, ax=axes[1])
    res["r2"] = {"train": _.train_score_, "test": _.test_score_}
    res["fig"] = fig
    if return_model:
        res["model"] = model
    return res


# from sklearn.preprocessing import KBinsDiscretizer


# def categoricalize(x, n_bins=5):
#     cls = KBinsDiscretizer(n_bins=n_bins, encode="ordinal")
#     _ = cls.fit_transform(x.values.reshape(-1, 1)).reshape(-1).astype(int)
#     return pd.Categorical(_), cls


# def vis_model_classifier(model, X_train, y_train, X_test, y_test, return_model=False):
#     import re
#     from yellowbrick.classifier.rocauc import roc_auc
#     from yellowbrick.classifier import precision_recall_curve, class_prediction_error
#     from yellowbrick.classifier import classification_report, confusion_matrix

#     pre = re.sub(r"[^A-Z]", "", str(model)) + "_"
#     res = dict()
#     fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(12, 12))
#     _ = roc_auc(
#         model, X_train, y_train, X_test=X_test, y_test=y_test, show=False, ax=axes[0]
#     )
#     res[pre + "roc_auc"] = _.roc_auc
#     _ = precision_recall_curve(
#         model, X_train, y_train, X_test, y_test, per_class=True, show=False, ax=axes[1]
#     )

#     res[pre + "prec_recall"] = _.score_
#     class_prediction_error(
#         model, X_train, y_train, X_test, y_test, show=False, ax=axes[2]
#     )
#     confusion_matrix(model, X_train, y_train, X_test, y_test, show=False, ax=axes[3])
#     classification_report(
#         model, X_train, y_train, X_test, y_test, support=True, show=False, ax=axes[4]
#     )
#     if return_model:
#         res["model"] = model
#     return res, fig


from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor, LGBMClassifier


def quick_regressor(X, y, return_model=False):
    models = [
        LinearRegression(),
        RandomForestRegressor(max_depth=5),
    ]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=True
    )
    return [
        vis_model_regression(
            model, X_train, y_train, X_test, y_test, return_model=return_model
        )
        for model in models
    ]


# def quick_classifier(X, y, n_class=5, return_model=False):
#     models = [
#         RandomForestClassifier(max_depth=5, criterion="log_loss"),
#         LGBMClassifier(boosting_type="gbdt", max_depth=5, verbose=-1),
#     ]

#     y_, cls = categoricalize(y, n_class)
#     X_train, X_test, y_train, y_test = train_test_split(
#         X, y_, test_size=0.2, shuffle=True
#     )
#     return [
#         vis_model_classifier(
#             model, X_train, y_train, X_test, y_test, return_model=return_model
#         )
#         for model in models
#     ] + [cls]


def summary_model_sk(model, x, y):
    model.fit(x, y)
    res = {
        #        'model': model,
        "score": model.score(x, y),
        "intercept": model.intercept_,
        "coef": model.coef_.tolist(),
        #        'predict':model.predict(x),
        "params": model.get_params(),
    }
    return res


main()
