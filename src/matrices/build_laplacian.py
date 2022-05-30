from typing import Union

import numpy as np
from scipy.sparse import csr_matrix, coo_matrix

from src.mesh.mesh import Mesh
from src.sparse_format import SparseFormat


def build_laplacian(mesh: Mesh,
                    link_exponents: Union[np.ndarray, None] = None,
                    fixed_sites: Union[np.ndarray, None] = None,
                    fixed_sites_eigenvalues: float = 1,
                    sparse_format: SparseFormat = SparseFormat.CSR
                    ) -> csr_matrix:
    """
    Build a Laplacian matrix on a given mesh. The default boundary condition is
    homogenous Neumann conditions. To get
    Dirichlet conditions add fixed sites. To get non-homogenous Neumann
    condition the flux need to be specified
    using a Neumann boundary Laplacian matrix.
    :param mesh: The mesh.
    :param link_exponents: The value is integrated, exponentiated and used as a
    link variable.
    :param fixed_sites: The sites to hold fixed.
    :param fixed_sites_eigenvalues: The eigenvalues for the fixed sites.
    :param sparse_format: Sparse format used to save the data.
    :return: The Laplacian matrix.
    """

    edge_mesh = mesh.edge_mesh

    # Compute the weights for each edge
    weights = edge_mesh.dual_edge_lengths / edge_mesh.edge_lengths

    # Compute the link variable weights
    link_variable_weights = np.exp(
        -1j * (link_exponents * edge_mesh.directions).sum(axis=1)
    ) if link_exponents is not None else np.ones(len(weights))

    # Rows and cols to update
    rows = np.concatenate([
        edge_mesh.edges[:, 0],
        edge_mesh.edges[:, 1],
        edge_mesh.edges[:, 0],
        edge_mesh.edges[:, 1]
    ])

    cols = np.concatenate([
        edge_mesh.edges[:, 1],
        edge_mesh.edges[:, 0],
        edge_mesh.edges[:, 0],
        edge_mesh.edges[:, 1]
    ])

    # The values
    values = np.concatenate([
        weights * link_variable_weights / mesh.areas[edge_mesh.edges[:, 0]],

        weights *
        link_variable_weights.conjugate() / mesh.areas[edge_mesh.edges[:, 1]],

        - weights / mesh.areas[edge_mesh.edges[:, 0]],

        - weights / mesh.areas[edge_mesh.edges[:, 1]]
    ])

    # Build the Laplacian
    laplacian = coo_matrix((values, (rows, cols)),
                           shape=(len(mesh.x), len(mesh.x)))

    # Change the rows corresponding to fixed sites to identity
    if fixed_sites is not None:
        # Convert laplacian to list of lists
        # This makes it quick to do slices
        laplacian = laplacian.tolil()

        # Change the rows corresponding to the fixed sites
        laplacian[fixed_sites, :] = 0
        laplacian[fixed_sites, fixed_sites] = fixed_sites_eigenvalues

    return laplacian.asformat(sparse_format.value, copy=False)
