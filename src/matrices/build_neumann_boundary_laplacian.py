from typing import Union

from scipy.sparse import csr_matrix, coo_matrix
import numpy as np

from src.mesh.mesh import Mesh


def build_neumann_boundary_laplacian(mesh: Mesh,
                                     fixed_sites: Union[np.ndarray, None] = None
                                     ) -> csr_matrix:
    """
    Build extra matrix for the Laplacian to set non-homogenous Neumann
    boundary conditions.
    :param mesh: The mesh.
    :param fixed_sites: The fixed sites.
    :return: The Neumann boundary matrix.
    """

    edge_mesh = mesh.edge_mesh

    boundary_index = np.arange(len(edge_mesh.boundary_edge_indices))

    # Get the boundary edges which are stored in the beginning of
    # the edge vector
    boundary_edges = edge_mesh.edges[edge_mesh.boundary_edge_indices]
    boundary_edges_length = edge_mesh.edge_lengths[
        edge_mesh.boundary_edge_indices
    ]

    # Rows and cols to update
    rows = np.concatenate([
        boundary_edges[:, 0],
        boundary_edges[:, 1]
    ])

    cols = np.concatenate([
        boundary_index,
        boundary_index
    ])

    # The values
    values = np.concatenate([
        boundary_edges_length / (2 * mesh.areas[boundary_edges[:, 0]]),
        boundary_edges_length / (2 * mesh.areas[boundary_edges[:, 1]])
    ])

    # Build the matrix
    neumann_laplacian = coo_matrix((values, (rows, cols)),
                                   shape=(len(mesh.x), len(boundary_index)))

    # Change the rows corresponding to fixed sites to identity
    if fixed_sites is not None:
        # Convert laplacian to list of lists
        # This makes it quick to do slices
        neumann_laplacian = neumann_laplacian.tolil()

        # Change the rows corresponding to the fixed sites
        neumann_laplacian[fixed_sites, :] = 0

    return neumann_laplacian.tocsr()
