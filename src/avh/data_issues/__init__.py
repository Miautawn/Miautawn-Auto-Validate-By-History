import math
from typing import Tuple, List, Union, Any, Dict, Iterable
import multiprocessing as mp
from itertools import product
import pickle

import pandas as pd
import numpy as np
from tqdm import tqdm
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.utils.validation import check_is_fitted

from avh.aliases import Seed
from avh.data_issues._base import IssueTransfomer, NumericIssueTransformer, CategoricalIssueTransformer
from avh.data_issues._issues import SchemaChange, IncreasedNulls, VolumeChangeUpsample, VolumeChangeDownsample, DistributionChange
from avh.data_issues._numeric import UnitChange, NumericPerturbation
from avh.data_issues._categorical import CasingChange
from avh.data_issues._dataset import DQIssueDatasetGenerator

"""
Provides the 'issue transformers', which can be used to simulate data quality issues 
    for the AVH algorithm. 

Note: not all issue transformers are identical in their functionality to the original paper's:
    https://github.com/microsoft/Auto-Validate-by-History/blob/main/gene_sample.py

    Here are the main differences:
        * IncreasedNulls - In the author's code, a bunch of nulls are appended
            to the original column. In our implementation we replace values with nulls instead.
            This way we try to isolate the effect of null increase, rather than a combination of
            null and row count increase.
        * DistributionChange - In the author's code, only the last/first p% of rows are taken
            to simulate the distribution shift. In our implementation we tile 
            the last/first p% of values across all rows.
            This way we try to isolate the effect of distribution shift.
"""

__all__ = [
    "IssueTransfomer",
    "SchemaChange",
    "IncreasedNulls",
    "VolumeChangeUpsample",
    "VolumeChangeDownsample",
    "DistributionChange",
    "NumericIssueTransformer",
    "UnitChange",
    "NumericPerturbation",
    "CategoricalIssueTransformer",
    "CasingChange"
    "DQIssueDatasetGenerator"
]




