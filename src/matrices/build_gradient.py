from typing import Union

import numpy as np
from scipy.sparse import coo_matrix

from src.mesh.mesh import Mesh


def build_gradient(mesh: Mesh, link_exponents: Union[np.ndarray, None] = None):
    """
    Build the gradient for a function living on the sites onto the edges.
    :param mesh: The mesh.
    :param link_exponents: The value is integrated, exponentiated and used as
    a link variable.
    :return: The gradient matrix.
    """

    edge_mesh = mesh.edge_mesh

    # Indices for each edge
    edge_indices = np.arange(len(edge_mesh.edges))

    # Compute the weights for each edge
    weights = 1 / edge_mesh.edge_lengths

    # Compute the link variable weights
    link_variable_weights = np.exp(
        -1j * (np.asarray(link_exponents) * edge_mesh.directions).sum(axis=1)
    ) if link_exponents is not None else np.ones(len(weights))

    # Rows and cols to update
    rows = np.concatenate([
        edge_indices,
        edge_indices
    ])

    cols = np.concatenate([
        edge_mesh.edges[:, 1],
        edge_mesh.edges[:, 0]
    ])

    # The values
    values = np.concatenate([
        link_variable_weights * weights,
        - weights
    ])

    return coo_matrix((values, (rows, cols)),
                      shape=(len(edge_mesh.edges), len(mesh.x))).tocsr()
