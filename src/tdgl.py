import numpy as np
from scipy.sparse import csr_matrix

from src.mesh.mesh import Mesh
from src.util.sum_contributions import sum_contributions


def get_supercurrent(psi: np.ndarray,
                     gradient: csr_matrix,
                     edges: np.ndarray
                     ) -> np.ndarray:
    """
    Compute the supercurrent on the edges.
    :param psi: The value of the complex order parameter.
    :param gradient: The covariant derivative matrix.
    :param edges: The indices for the edges.
    :return: The supercurrent at each edge.
    """
    return ((gradient @ psi) * psi.conjugate()[edges[:, 0]]).imag


def get_observable_on_site(observable_on_edge: np.ndarray,
                           mesh: Mesh
                           ) -> np.ndarray:
    """
    Compute the observable on site.
    :param observable_on_edge: Observable on the edges.
    :param mesh: The corresponding mesh.
    :return: The observable vector at each site.
    """

    # Normalize the edge direction
    normalized_directions = mesh.edge_mesh.directions / np.linalg.norm(
        mesh.edge_mesh.directions,
        axis=1
    )[:, None]

    # Flux
    flux_x = observable_on_edge * normalized_directions[:, 0]
    flux_y = observable_on_edge * normalized_directions[:, 1]

    # Sum x and y components for every edge connecting to the vertex
    vertices = np.concatenate([
        mesh.edge_mesh.edges[:, 0],
        mesh.edge_mesh.edges[:, 1],
        mesh.boundary_indices
    ])

    x_values = np.concatenate([
        flux_x,
        flux_x,
        np.zeros_like(mesh.boundary_indices)
    ])

    y_values = np.concatenate([
        flux_y,
        flux_y,
        np.zeros_like(mesh.boundary_indices)
    ])

    vertex_group, x_group_values, counts = sum_contributions(vertices, x_values)
    idx = np.argsort(vertex_group)
    x_group_values = (x_group_values / counts)[idx]

    vertex_group, y_group_values, counts = sum_contributions(vertices, y_values)
    idx = np.argsort(vertex_group)
    y_group_values = (y_group_values / counts)[idx]

    return np.array([
        x_group_values / 2,
        y_group_values / 2
    ]).transpose()
