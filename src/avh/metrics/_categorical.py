from abc import ABC, abstractmethod
from typing import List, Union, Any
import time
from scipy.stats import wasserstein_distance

import pandas as pd
import numpy as np

from avh.metrics._base import Metric, SingleDistributionMetric, TwoDistributionMetric, NumericMetricMixin, CategoricalMetricMixin

#### Single distribution metrics

class DistinctCount(CategoricalMetricMixin, SingleDistributionMetric):
    @classmethod
    def _calculate(self, column: pd.Series) -> float:
        return column.nunique(dropna=False)


class MeanStringLength(CategoricalMetricMixin, SingleDistributionMetric):
    @classmethod
    def _calculate(self, column: pd.Series) -> float:
        if self._is_empty(column):
            return 0.0
        return np.nanmean(column.str.len())

class MeanDigitLength(CategoricalMetricMixin, SingleDistributionMetric):
    @classmethod
    def _calculate(self, column: pd.Series) -> float:
        if self._is_empty(column):
            return 0.0
        return np.nanmean(column.str.count(r"\d"))


class MeanPunctuationLength(CategoricalMetricMixin, SingleDistributionMetric):
    @classmethod
    def _calculate(self, column: pd.Series) -> float:
        if self._is_empty(column):
            return 0.0
        return np.nanmean(column.str.count(r"[!\"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]"))