from typing import Sequence, Tuple

import h5py
import numpy as np

from src.mesh.dual_mesh import DualMesh
from src.mesh.util.dual_edge_length import get_dual_edge_lengths
from src.mesh.util.find_edges import get_edges


class EdgeMesh:
    """
    Mesh for the edges in the original mesh.
    """

    def __init__(self,
                 x: Sequence[float],
                 y: Sequence[float],
                 edges: Sequence[Tuple[int, int]],
                 boundary_edge_indices: Sequence[int],
                 directions: Sequence[Tuple[float, float]],
                 edge_lengths: Sequence[float],
                 dual_edge_lengths: Sequence[float]):
        """
        Create the edge mesh.

        NOTE: Use from_mesh factory method to create from mesh.

        :param x: Coordinates for the mesh points.
        :param y: Coordinates for the mesh points.
        :param edges: The edges as a sequence of indices.
        :param boundary_edge_indices: Edges on the boundary.
        :param directions: Directions of the edges.
        :param edge_lengths: Lengths of the edges.
        :param dual_edge_lengths: Length of the edge duals.
        """

        self.x = np.asarray(x)
        self.y = np.asarray(y)
        self.edges = np.asarray(edges)
        self.boundary_edge_indices = np.asarray(boundary_edge_indices)
        self.directions = np.asarray(directions)
        self.edge_lengths = np.asarray(edge_lengths)
        self.dual_edge_lengths = np.asarray(dual_edge_lengths)

    @classmethod
    def from_mesh(cls,
                  x: np.ndarray,
                  y: np.ndarray,
                  elements: np.ndarray,
                  dual_mesh: DualMesh
                  ) -> 'EdgeMesh':
        """
        Create edge mesh from mesh.

        :param x: Coordinates for the mesh points.
        :param y: Coordinates for the mesh points.
        :param elements: Elements for the mesh.
        :param dual_mesh: The dual mesh.
        :return: The edge mesh.
        """

        # Get the edges and the boundary edges
        edges, is_boundary = get_edges(elements)

        # Get the indices of the boundary edges
        boundary_edge_indices = is_boundary.nonzero()[0]

        # Get the coordinates
        xe = np.mean(x[edges], axis=1)
        ye = np.mean(y[edges], axis=1)

        # Get the directions
        directions = np.concatenate([
            np.diff(x[edges], axis=1),
            np.diff(y[edges], axis=1)
        ], axis=1)

        # Get the lengths of the edges
        edge_lengths = np.linalg.norm(directions, axis=1)

        # Get the lengths of the edge duals
        dual_edge_lengths = get_dual_edge_lengths(
            xe=xe,
            ye=ye,
            elements=elements,
            x_dual=dual_mesh.x,
            y_dual=dual_mesh.y,
            edges=edges
        )

        return EdgeMesh(xe, ye, edges, boundary_edge_indices, directions,
                        edge_lengths, dual_edge_lengths)

    def get_boundary_edges(self) -> np.ndarray:
        """
        Get the boundary edges.
        :return: The boundary edges.
        """
        return self.edges[self.boundary_edge_indices, :]

    def save_to_hdf5(self, h5group: h5py.Group):
        """
        Save the data to a HDF5 file.
        :param h5group: The HDF5 group to write the data to.
        """
        h5group['x'] = self.x
        h5group['y'] = self.y
        h5group['edges'] = self.edges
        h5group['boundary_edge_indices'] = self.boundary_edge_indices
        h5group['directions'] = self.directions
        h5group['edge_lengths'] = self.edge_lengths
        h5group['dual_edge_lengths'] = self.dual_edge_lengths

    @classmethod
    def load_from_hdf5(cls, h5group: h5py.Group) -> 'EdgeMesh':
        """
        Load edge mesh from file.
        :param h5group: The HDF5 group to load from.
        :return: The loaded edge mesh.
        """

        if not('x' in h5group and 'y' in h5group and 'edges' in h5group
               and 'boundary_edge_indices' in h5group
               and 'directions' in h5group and 'edge_lengths' in h5group
               and 'dual_edge_lengths' in h5group):
            raise IOError('Could not load edge mesh due to missing data.')

        return EdgeMesh(
            x=h5group['x'],
            y=h5group['y'],
            edges=h5group['edges'],
            boundary_edge_indices=h5group['boundary_edge_indices'],
            directions=h5group['directions'],
            edge_lengths=h5group['edge_lengths'],
            dual_edge_lengths=h5group['dual_edge_lengths']
        )

