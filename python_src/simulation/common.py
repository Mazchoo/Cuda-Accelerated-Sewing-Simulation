""" Common interfaces for passing information in simulation """
from typing import NamedTuple, List, Iterable, Tuple

import numpy as np


class DistanceAdjustment(NamedTuple):
    """
        An adjustment made outside of forces directly to distance
        Resolving too many forces can make the model less stable
        so it is better to handle collisions with adjustments
    """
    indices: List[np.ndarray]
    amounts: List[np.ndarray]

    def __iter__(self) -> Iterable[Tuple[np.ndarray, np.ndarray]]:
        """ Iterate through each adjustment, indices and amounts """
        yield from zip(self.indices, self.amounts)
