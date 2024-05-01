from typing import List, Tuple, Optional
from abc import ABC, abstractmethod

import pandas as pd
import numpy as np
from gutenbergpy import textget

from avh.data_generation._base import DataColumn, NumericColumn, CategoricalColumn

# predownloading Moby-dick text for random text generation
raw_book = textget.get_text_by_id(2701)
raw_book = str(textget.strip_headers(raw_book)).replace("\\n", "")


class StaticCategoricalColumn(CategoricalColumn):
    """
    Concrete categorical column class.
    Outputs the column populated by provided values.

    Parameters
    ----------
    name: str
        The name of the column in the final output
    values: List[str]
        A list of values which the column will output.
        The list of values must be equal in length to requested column size.
    **kwargs:
        Any other parameters will be forwarded back to parent classes
    """

    def __init__(self, name: str, values: List[str], **kwargs):
        super().__init__(name, **kwargs)
        self._values = values

    def _generate(self, n: int) -> np.array:
        assert n == len(self._values), (
            f"The StaticCategoricalColumn does not have equal number of values "
            f"to fill a column of size {n}"
        )
        return np.array(self._values, dtype="object")


class RandomCategoricalColumn(CategoricalColumn):
    """
    Concrete categorical column class.
    Outputs the column randomly populated by a pool of values.

    Parameters
    ----------
    name: str
        The name of the column in the final output
    values: Optional[List[str]]
        A list of values which will be used to randomly populate the column.
        If None, the class will output random lorem sentences.
    **kwargs:
        Any other parameters will be forwarded back to parent classes
    """

    def __init__(self, name: str, values: Optional[List[str]] = None, **kwargs):
        super().__init__(name, **kwargs)
        self._values = values

    def _generate(self, n: int) -> np.array:
        rng = np.random.default_rng(self.random_state)
        if self._values:
            return rng.choice(self._values, n, replace=True)
        else:
            random_idx = rng.integers(0, len(raw_book) - 20, n)
            return np.array(
                [raw_book[random_idx[i] : random_idx[i] + 20] for i in range(n)]
            )