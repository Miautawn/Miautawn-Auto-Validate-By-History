"""
Full credit goes to:

Sebastian Schmidl, Phillip Wenig, and Thorsten Papenbrock.
Anomaly Detection in Time Series: A Comprehensive Evaluation.
PVLDB, 15(9): 1779 - 1797, 2022. doi:10.14778/3538598.3538602

The code was borrowed straight from their repository at:
https://github.com/TimeEval/TimeEval-algorithms/tree/main/health_esn
"""

from enum import Enum
from typing import Callable, List, Optional, Tuple

import numpy as np
import tqdm
from scipy import sparse
from scipy.special import expit
from sklearn.base import BaseEstimator, OutlierMixin, TransformerMixin
from sklearn.linear_model import LinearRegression


class Activation(Enum):
    SIGMOID = "sigmoid"
    TANH = "tanh"

    def get_fun(self) -> Callable[[np.ndarray], np.ndarray]:
        if self == Activation.SIGMOID:
            return expit
        else:  # if self == Activation.TANH
            return np.tanh


class Reservoir(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        input_size: int,
        output_size: int,
        hidden_units: int,
        connectivity: float,
        spectral_radius: float,
        activation: Callable[[np.ndarray], np.ndarray],
    ):
        super().__init__()

        self.hidden_units = hidden_units
        self.activation = activation
        self.W_in = np.random.uniform(-0.1, 0.1, (input_size, hidden_units))
        self.W_s = self._initialize_internal_weights(hidden_units, connectivity, spectral_radius)
        self.W_fb = np.random.uniform(-0.1, 0.1, (output_size, hidden_units))

    def _initialize_internal_weights(
        self, n_internal_units, connectivity, spectral_radius
    ) -> np.ndarray:
        # Generate sparse, uniformly distributed weights.
        internal_weights = sparse.rand(
            n_internal_units, n_internal_units, density=connectivity
        ).todense()

        # Ensure that the nonzero values are uniformly distributed in [-0.5, 0.5]
        internal_weights[np.where(internal_weights > 0)] -= 0.5

        # Adjust the spectral radius.
        E, _ = np.linalg.eig(internal_weights)
        e_max = np.max(np.abs(E))
        internal_weights /= np.abs(e_max) / spectral_radius

        return internal_weights

    def _calc_state(self, x: np.ndarray, last_state: np.ndarray, last_output: np.ndarray):
        state = x.dot(self.W_in) + last_state.dot(self.W_s) + last_output.dot(self.W_fb)
        state = self.activation(state)
        return state

    def fit_transform(
        self,
        X: Tuple[np.ndarray, Optional[np.ndarray], Optional[np.ndarray]],
        y=None,
        **fit_params
    ) -> np.ndarray:
        """
        :param X: all Xs need the following shapes (batch_size, n_components)np.ndarray
                  and are expected to be (input, last_state, last_output)
        :param y: not needed
        :param fit_params: not needed
        :return: `window_size` outputs of the Reservoir
        """

        current_input, last_state, last_output = X

        if last_state is None and last_output is None:
            last_state = np.zeros((1, self.hidden_units))
            last_output = np.zeros_like(current_input)

        state = self._calc_state(current_input, last_state, last_output)
        return state


class HealthESN(BaseEstimator, OutlierMixin):
    def __init__(
        self,
        n_dimensions: int,
        hidden_units: int,
        window_size: int,
        connectivity: float,
        spectral_radius: float,
        activation: Callable[[np.ndarray], np.ndarray],
        seed: int,
    ):
        super().__init__()

        np.random.seed(seed)

        self.esn = Reservoir(
            n_dimensions, n_dimensions, hidden_units, connectivity, spectral_radius, activation
        )
        self.w_out = LinearRegression()
        self.window_size = window_size
        sigma = np.arange(self.window_size)[::-1]
        self.sigma = sigma / sigma.sum()

    def fit(self, X: np.ndarray) -> "HealthESN":
        y = X[1:]
        x = X[:-1]

        last_state = None
        last_output = None
        states: List[np.ndarray] = []
        for t in tqdm.trange(x.shape[0], disable=True):
            x_ = (x[[t]], last_state, last_output)
            state = self.esn.fit_transform(x_)
            states.append(state)
            last_state = state
            last_output = y[[t]]

        concat_states = np.asarray(np.concatenate(states, axis=0))
        self.w_out.fit(concat_states, y)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        states = []
        last_state = None
        last_output = None
        for i in tqdm.trange(self.window_size, X.shape[0], disable=True):
            for p in reversed(range(1, self.window_size + 1)):
                x = (X[i - p], last_state, last_output)
                state = self.esn.fit_transform(x, X[i - p + 1])
                last_state = state
                last_output = X[i - p + 1]
            states.append(last_state)

        concat_states = np.asarray(np.concatenate(states, axis=0))
        outputs = self.w_out.predict(concat_states)

        scores = np.linalg.norm(X[self.window_size :] - outputs, axis=1)
        scores = np.concatenate([np.zeros(X.shape[0] - scores.shape[0]) + np.nan, scores])

        return scores

    def fit_predict(self, X, y=None):
        self.fit(X)
        return self.predict(X)
