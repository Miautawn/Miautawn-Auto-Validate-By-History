from abc import ABC, abstractmethod
from typing import List, Union, Any
import time
from scipy.stats import wasserstein_distance, 

import pandas as pd
import numpy as np

from avh.metrics._base import Metric, SingleDistributionMetric, TwoDistributionMetric

#### Single distribution metrics

class RowCount(SingleDistributionMetric):
    @classmethod
    def _calculate(self, column: pd.Series) -> float:
        return len(column)

class DistinctRatio(SingleDistributionMetric):
    """
    I don't like that this is also a numeric metric!
    Since it's almost always treated as a statistical invariate
    because yeah, floating point numbers will mostly be unique all the time!!!
    """

    @classmethod
    def _calculate(self, column: pd.Series) -> float:
        return column.nunique(dropna=False) / len(column)

class CompleteRatio(SingleDistributionMetric):
    @classmethod
    def _calculate(self, column: pd.Series) -> float:
        if column.empty:
            return 0.0
        return column.count() / column.size
    
#### Two distribution metrics

    

    