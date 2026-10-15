import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin


class FuelMeanRegressor(BaseEstimator, RegressorMixin):
    """Baseline: predict the training mean of the target for each fuel class.

    Expects a binary feature column ``fuel_col`` (1 = Methanol, 0 = Heptane).
    This is the "mean per fuel" baseline required for the regression task.
    """

    def __init__(self, fuel_col="fuel_methanol"):
        self.fuel_col = fuel_col

    def fit(self, X, y):
        y = np.asarray(y, dtype=float)
        m = np.asarray(X[self.fuel_col]) == 1
        fallback = float(np.nanmean(y))
        self.mean_methanol_ = float(np.nanmean(y[m])) if m.any() else fallback
        self.mean_heptane_ = float(np.nanmean(y[~m])) if (~m).any() else fallback
        self.global_mean_ = fallback
        return self

    def predict(self, X):
        m = np.asarray(X[self.fuel_col]) == 1
        return np.where(m, self.mean_methanol_, self.mean_heptane_)
