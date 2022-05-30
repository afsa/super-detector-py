from typing import Tuple

import numpy as np


def get_edges(elements: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Find the edges from a list of triangles.
    :param elements: The triangle elements.
    :return: A tuple containing the edges and if they are a boundary edge.
    """

    # Separate the elements into the three edges of the triangles
    edges = np.concatenate([
        elements[:, (0, 1)],
        elements[:, (1, 2)],
        elements[:, (2, 0)]
    ])

    # Sort each edge such that the smallest index is first
    edges = np.sort(edges, axis=1)

    # Remove the duplicates of the edges
    edges, occurrences = np.unique(edges, return_counts=True, axis=0)

    return edges, occurrences == 1
