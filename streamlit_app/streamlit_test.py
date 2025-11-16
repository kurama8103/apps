# %%
import japanize_matplotlib
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import statsmodels.api as sm
import datetime as dt
import quantstats as qs
import myfunc.finfunc as mff

# pd.options.display.max_rows = 100
# pd.options.display.max_columns = 100
# pd.options.display.width = 120
pd.options.display.float_format = "{:,.4f}".format
np.set_printoptions(suppress=True)  # 指数表記
np.set_printoptions(precision=4)

sns.set_style("whitegrid")
japanize_matplotlib.japanize()

plt.figure()
plt.rcParams["figure.figsize"] = 12, 3


def load_data():
    # df = pd.read_pickle('files/stooq.pickel')
    # df.columns = [
    #     'equity_US', 'equity_DEV', 'equity_EM', 'bond_US', 'bond_DEV', 'bond_EM',
    #     'bond_TIPS', 'reit', 'gold', 'commodity', 'bitcoin']

    df = pd.read_csv("files/get_stooq.csv", index_col=0, parse_dates=True)

    df = df.dropna(how="all").ffill()
    df = ((df.T / df["FXY"]).T).drop("FXY", axis=1)
    return df


df = load_data().asfreq("D", method="ffill")["2021-12-31":"2022-12-31"]
dfm = df.asfreq("M", method="ffill")
(df / df.iloc[0]).plot()
# %%
x = df.iloc[:, 0]

# trend
# x_=pd.Series((np.arange(len(x))+1)).pct_change()
# mean reversion
# x_=pd.DataFrame(np.sin(np.arange(len(x))),x.index)

x_ = x.pct_change().dropna()
x
# %%
from numpy.lib.stride_tricks import sliding_window_view
import scipy


def momentum(x, window=None):
    if window == None:
        window = len(x)
    r = np.cumprod(x[-window - 2 : -1] + 1)
    mom = r[-1] / r[0] - 1
    return x[-1] - mom


def moving_window(x, window: int, func) -> list:
    # return [func(x[i : i + window]) for i in range(len(x) + 1 - window)]
    return [func(d) for d in sliding_window_view(x, window)]


def moving_window_df(x: pd.DataFrame, window: int, func) -> pd.DataFrame:
    return pd.DataFrame(
        moving_window(x.values, window, func), index=x.tail(len(x) + 1 - window).index
    )


# %%
from scipy.stats import gmean


def _f(x):
    n = 252
    m = np.mean(x) * n
    # m = gmean(1 + x) - 1
    s = np.std(x) * np.sqrt(n)
    d = {
        "mean": m,
        "std": s,
        "sharpe": (m / s),
        "skew": scipy.stats.skew(x),
        "kurt": scipy.stats.kurtosis(x),
        "hurst": mff.hurst(x)[0],
        "mom": momentum(x),
        # "cvar": mff.cvar(x)[1],
        # "adf":mff.adf_summary(x)['adf'],
    }
    return d


_ = pd.concat(
    [
        (x_ + 1).cumprod(),
        mff.max_draw_down(x),
        moving_window_df(x_, 180, _f),
    ],
    axis=1,
)
_.plot(subplots=True, figsize=(10, 8))
print(_.dropna())
# %%
# qs.plots.drawdowns_periods(x_)
# qs.plots.drawdown(x_)
# qs.plots.rolling_volatility(x_)
# qs.plots.rolling_sharpe(x_)
# qs.plots.histogram(x_)
qs.plots.monthly_heatmap(x_, square=True)
# %%
met = qs.reports.metrics(x_, display=False)
met.loc[
    [
        "Start Period",
        "End Period",
        "Risk-Free Rate",
        "Cumulative Return",
        "All-time (ann.)",
        "CAGR﹪",
        "Sharpe",
        "Prob. Sharpe Ratio",
        "MTD",
        "3M",
        "6M",
        "YTD",
        "1Y",
        "3Y (ann.)",
        "5Y (ann.)",
        "10Y (ann.)",
        "Max Drawdown",
        "Longest DD Days",
        "Avg. Drawdown",
        "Avg. Drawdown Days",
    ]
]
# %%
x_.plot(kind="hist", bins=12)
x_.plot(kind="kde", secondary_y=True)
# %%
count, division = np.histogram(x_, bins=12)
plt.bar(x=division[1:], height=count, width=0.0072)

# %%
n = -1
_ = dfm.iloc[n] / dfm.iloc[[n - 1, n - 3, n - 6, n - 12]] - 1
_.index = ["1M", "3M", "6M", "12M"]
sns.heatmap(_.T, center=0, annot=True, fmt=".1%", cmap="PiYG")
# %%
sns.clustermap(
    df.pct_change().corr(),
    figsize=(8, 4),
    col_cluster=False,
    annot=True,
    fmt=".2f",
    center=0,
    cmap="RdBu_r",
)

# %%
import riskfolio as rp

# method_mu='hist' # Method to estimate expected returns based on historical data.
# method_cov='hist' # Method to estimate covariance matrix based on historical data.


def calc_pf_weight(returns):
    port = rp.Portfolio(returns=returns)
    port.assets_stats(method_mu="hist", method_cov="hist", d=0.94)
    model = "Classic"  # Could be Classic (historical), BL (Black Litterman) or FM (Factor Model)
    hist = True  # Use historical scenarios for risk measures that depend on scenarios
    rf = 0  # Risk free rate
    l = 0  # Risk aversion factor, only useful when obj is 'Utility'

    rms = [
        "MV",
        # 'CVaR', 'MAD', 'MSV', 'FLPM', 'SLPM','EVaR', 'WR', 'MDD', 'ADD', 'CDaR', 'UCI', 'EDaR'
    ]  # Risk measure used, this time will be variance
    objs = [
        "Sharpe",
        "MinRisk",
    ]  # Objective function, could be MinRisk, MaxRet, Utility or Sharpe
    cols = []

    w_s = pd.DataFrame([])

    for obj in objs:
        for rm in rms:
            w = port.optimization(model=model, rm=rm, obj=obj, rf=rf, l=l, hist=hist)
            w_s = pd.concat([w_s, w], axis=1)
            cols.append(obj + "_" + rm)
    w_s.columns = cols
    w_s["RP"] = port.rp_optimization(model=model, rm=rm, rf=rf, b=None, hist=hist)
    w_s["EQ"] = [1 / df.shape[1]] * df.shape[1]
    return w_s


dfr = df.pct_change().dropna()
w_s = calc_pf_weight(returns=dfr)
w_s.style.format("{:.2%}")
# %%
pf_type = "Sharpe_MV"
rp.plot_pie(
    w=w_s[[pf_type]],
    title=pf_type,
    others=0.05,
    nrow=25,
    cmap="tab20",
    height=4,
    width=10,
    ax=None,
)
plt.figure()
rp.plot_risk_con(
    w_s[[pf_type]],
    cov=dfr.cov(),
    returns=dfr,
    rm="MV",
    rf=0,
    alpha=0.01,
    color="tab:blue",
    height=2,
    width=10,
    ax=None,
)
# %%
((dfm.pct_change() @ w_s).fillna(0) + 1).cumprod().plot()
(dfm / dfm.iloc[0]).plot()
# %%
