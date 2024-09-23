import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, LassoCV

import pandas as pd
import streamlit as st
from st_util import load_csv, format_df

plt.rcParams["figure.figsize"] = 8, 4
# import seaborn as sns
# sns.set_style("whitegrid")
import japanize_matplotlib

japanize_matplotlib.japanize()


def main():
    df_ = load_csv()
    if df_ is not None:
        df_=df_.dropna()
        if st.checkbox("Use percentage change (return) data",True):
            df_=df_.pct_change().dropna()
            
        X = df_.iloc[:, 1:]
        y = df_.iloc[:, 0]

        st.text("target: " + y.name)
        st.text("features: " + ", ".join(X.columns.values))

        if X.shape[1]>1:
            st.markdown("features component plot")
            res = vis_features(X, y)
            st.pyplot(res)

        st.markdown("model: LightGBM")
        res = quick_regressor(X, y)
        st.pyplot(res[1]["fig"])
        st.json(res[1])


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


from sklearn.preprocessing import KBinsDiscretizer


def categoricalize(x, n_bins=5):
    cls = KBinsDiscretizer(n_bins=n_bins, encode="ordinal")
    _ = cls.fit_transform(x.values.reshape(-1, 1)).reshape(-1).astype(int)
    return pd.Categorical(_), cls


def vis_model_classifier(model, X_train, y_train, X_test, y_test, return_model=False):
    import re
    from yellowbrick.classifier.rocauc import roc_auc
    from yellowbrick.classifier import precision_recall_curve, class_prediction_error
    from yellowbrick.classifier import classification_report, confusion_matrix

    pre = re.sub(r"[^A-Z]", "", str(model)) + "_"
    res = dict()
    fig, axes = plt.subplots(nrows=5, ncols=1, figsize=(12, 12))
    _ = roc_auc(
        model, X_train, y_train, X_test=X_test, y_test=y_test, show=False, ax=axes[0]
    )
    res[pre + "roc_auc"] = _.roc_auc
    _ = precision_recall_curve(
        model, X_train, y_train, X_test, y_test, per_class=True, show=False, ax=axes[1]
    )

    res[pre + "prec_recall"] = _.score_
    class_prediction_error(
        model, X_train, y_train, X_test, y_test, show=False, ax=axes[2]
    )
    confusion_matrix(model, X_train, y_train, X_test, y_test, show=False, ax=axes[3])
    classification_report(
        model, X_train, y_train, X_test, y_test, support=True, show=False, ax=axes[4]
    )
    if return_model:
        res["model"] = model
    return res, fig


from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from lightgbm import LGBMRegressor, LGBMClassifier
# import shap÷\

# shap.initjs()


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


def quick_classifier(X, y, n_class=5, return_model=False):
    models = [
        RandomForestClassifier(max_depth=5, criterion="log_loss"),
        LGBMClassifier(boosting_type="gbdt", max_depth=5, verbose=-1),
    ]

    y_, cls = categoricalize(y, n_class)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_, test_size=0.2, shuffle=True
    )
    return [
        vis_model_classifier(
            model, X_train, y_train, X_test, y_test, return_model=return_model
        )
        for model in models
    ] + [cls]


# def vis_shap(model, X):
#     print(model)
#     explainer = shap.TreeExplainer(model)
#     shap_values = explainer(X)

#     shap.summary_plot(shap_values)
#     # shap.summary_plot(shap_values, plot_type="bar")
#     return shap_values


def calc_regression(df_, flg=0):
    y = st.selectbox("Y", df_.columns)
    c = list(df_.columns.drop(y))
    x = st.multiselect("X", c, c)
    if len(x) == 0:
        st.stop()

    model = LinearRegression(fit_intercept=True)
    res = summary_model_sk(model, df_[x], df_[y])
    st.write(model, res["score"])
    st.json(res, expanded=False)

    model = LassoCV(fit_intercept=True, alphas=[0, 0.01, 0.1, 1, 10], cv=5)
    res = summary_model_sk(model, df_[x], df_[y])
    st.write(model, res["score"])
    st.json(res, expanded=False)

    pred = (df_[x] * res["coef"]).sum(axis=1) + res["intercept"]
    pred.name = "prediction"
    pred = pd.concat([pred, df_[y]], axis=1)
    if flg == 1:
        pred = (1 + pred).cumprod()
    st.line_chart(pred, height=200)


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
