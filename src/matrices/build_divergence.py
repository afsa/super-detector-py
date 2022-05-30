from scipy.sparse import csr_matrix, coo_matrix
import numpy as np

from src.mesh.mesh import Mesh


def build_divergence(mesh: Mesh) -> csr_matrix:
    """
    Build the divergence matrix that takes the divergence of a function living
    on the edge onto the sites.
    :param mesh: The mesh.
    :return: The divergence matrix.
    """

    edge_mesh = mesh.edge_mesh

    # Indices for each edge
    edge_indices = np.arange(len(edge_mesh.edges))

    # Compute the weights for each edge
    weights = edge_mesh.dual_edge_lengths

    # Rows and cols to update
    rows = np.concatenate([
        edge_mesh.edges[:, 0],
        edge_mesh.edges[:, 1]
    ])

    cols = np.concatenate([
        edge_indices,
        edge_indices
    ])

    # The values
    values = np.concatenate([
        weights / mesh.areas[edge_mesh.edges[:, 0]],
        - weights / mesh.areas[edge_mesh.edges[:, 1]]
    ])

    return coo_matrix((values, (rows, cols)),
                      shape=(len(mesh.x), len(edge_mesh.edges))).tocsr()
