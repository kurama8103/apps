import numpy as np

def hurst(series):
    """Returns the Hurst exponent of the time series vector series"""
    # Create the range of lag values
    lags = range(2, 100)

    # Calculate the array of the variances of the lagged differences
    tau = [np.sqrt(np.std(np.subtract(series[lag:], series[:-lag]))) for lag in lags]

    # Use a linear fit to estimate the Hurst exponent
    poly = np.polyfit(np.log(lags), np.log(tau), 1)

    # Return the Hurst exponent from the polyfit output
    return poly[0]*2.0, 0, 0 # c and data are dummy values

def cvar(series, confidence_level=0.95):
    """Calculates the Conditional Value at Risk (CVaR) of a time series"""
    var = np.percentile(series, (1 - confidence_level) * 100)
    cvar = series[series < var].mean()
    return var, cvar
