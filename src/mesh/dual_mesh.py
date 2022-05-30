from typing import Sequence

import h5py
import numpy as np

from src.mesh.util.voronoi import generate_voronoi_vertices


class DualMesh:
    """
    A dual Voronoi mesh.
    """

    def __init__(self,
                 x: Sequence[float],
                 y: Sequence[float]
                 ):
        """
        Create a dual mesh.

        NOTE: use the factory method from_mesh to create the dual from an
        existing mesh.

        :param x: Coordinates for the dual mesh points.
        :param y: Coordinates for the dual mesh points.
        """

        self.x = np.asarray(x)
        self.y = np.asarray(y)

    @classmethod
    def from_mesh(cls,
                  x: np.ndarray,
                  y: np.ndarray,
                  elements: np.ndarray
                  ) -> 'DualMesh':
        """
        Create a dual mesh from the mesh.

        :param x: Coordinates for the mesh points.
        :param y: Coordinates for the mesh points.
        :param elements: The mesh elements.
        :return: The dual mesh.
        """

        # Get the location of the Voronoi vertices from the original mesh
        xc, yc = generate_voronoi_vertices(x, y, elements)

        # Generate the dual mesh
        return DualMesh(xc, yc)

    def save_to_hdf5(self, h5group: h5py.Group):
        """
        Save the mesh to file.
        :param h5group: The HDF5 group to write to.
        """
        h5group['x'] = self.x
        h5group['y'] = self.y

    @classmethod
    def load_from_hdf5(cls, h5group: h5py.Group) -> 'DualMesh':
        """
        Load mesh from file.
        :param h5group: The HDF5 group to load from.
        :return: The loaded dual mesh
        """

        # Check if the mesh may be loaded
        if not ('x' in h5group and 'y' in h5group):
            raise IOError('Could not load dual mesh due to missing data.')

        return DualMesh(
            x=h5group['x'],
            y=h5group['y']
        )
