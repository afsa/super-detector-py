from enum import Enum
from typing import Sequence, Tuple, Callable, Any, Optional

import h5py
import numpy as np

from src.mesh.dual_mesh import DualMesh
from src.mesh.edge_mesh import EdgeMesh
from src.mesh.util.find_edges import get_edges
from src.mesh.util.voronoi import compute_surrounding_area, \
    get_surrounding_voronoi_polygons


class Operator(Enum):
    AND = np.all
    OR = np.any

    def __call__(self, *args, **kwargs) -> np.ndarray:
        return self.value(*args, **kwargs)


class Mesh:
    """
    A triangular mesh of a simply connected polygon.
    """

    def __init__(self,
                 x: Sequence[float],
                 y: Sequence[float],
                 elements: Sequence[Tuple[int, int, int]],
                 boundary_indices: Sequence[int],
                 areas: Sequence[float],
                 dual_mesh: DualMesh,
                 edge_mesh: EdgeMesh,
                 voltage_points: Optional[np.ndarray] = None,
                 input_edge: Optional[np.ndarray] = None,
                 output_edge: Optional[np.ndarray] = None):
        """
        Create the mesh from data.

        NOTE: Use Mesh.from_triangulation to create a new mesh.
        This constructor requires that all parameters to be known.
        :param x: The x coordinates for the triangle vertices.
        :param y: The x coordinates for the triangle vertices.
        :param elements: A list of triplets that correspond to the indices of
        the vertices that form a triangle.
        E.g. [[0, 1, 2], [0, 1, 3]] corresponds to a triangle connecting
        vertices 0, 1, and 2 and another triangle
        connecting vertices 0, 1, and 3.
        :param boundary_indices: Indices corresponding to the boundary.
        :param areas: The areas corresponding to the sites.
        :param dual_mesh: The dual mesh.
        :param edge_mesh: The edge mesh.
        :param voltage_points: Points to use when measuring voltage.
        :param input_edge: Location for the current input.
        :param output_edge: Location for the current output.
        """

        # Store the data
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        self.elements = np.asarray(elements)
        self.boundary_indices = np.asarray(boundary_indices)
        self.dual_mesh = dual_mesh
        self.edge_mesh = edge_mesh
        self.areas = np.asarray(areas)
        self.voltage_points = voltage_points
        self.input_edge = input_edge
        self.output_edge = output_edge

    @classmethod
    def from_triangulation(cls,
                           x: Sequence[float],
                           y: Sequence[float],
                           elements: Sequence[Tuple[int, int, int]],
                           voltage_points: Optional[np.ndarray] = None,
                           input_edge: Optional[np.ndarray] = None,
                           output_edge: Optional[np.ndarray] = None
                           ) -> 'Mesh':
        """
        Create a triangular mesh from the coordinates of the triangle vertices
        and a list of indices corresponding to
        the vertices that connect to triangles.
        :param x: The x coordinates for the triangle vertices.
        :param y: The x coordinates for the triangle vertices.
        :param elements: A list of triplets that correspond to the indices of
        the vertices that form a triangle.
        E.g. [[0, 1, 2], [0, 1, 3]] corresponds to a triangle connecting
        vertices 0, 1, and 2 and another triangle
        connecting vertices 0, 1, and 3.
        :param voltage_points: Points to use when measuring voltage.
        :param input_edge: Location for the current input.
        :param output_edge: Location for the current output
        """

        # Store the data
        x = np.asarray(x)
        y = np.asarray(y)
        elements = np.asarray(elements)

        # Make sure the x coordinates are in a one dimensional array
        if x.ndim != 1:
            raise ValueError(
                'The x coordinates need to be stored in '
                'an one dimensional array.'
            )

        # Make sure the y coordinates are in a one dimensional array
        if y.ndim != 1:
            raise ValueError(
                'The y coordinates need to be stored in '
                'an one dimensional array.'
            )

        # Make sure that the number of x coordinates are equal to the
        # number of y coordinates
        if np.size(x) != np.size(y):
            raise ValueError(
                'The number of x coordinates need to be equal to the '
                'number of y coordinates.'
            )

        # Make sure that the elements matrix is of dimension 2 and has
        # one length equal to 3
        if elements.ndim != 2 \
                or (elements.shape[0] != 3 and elements.shape[1] != 3):
            raise ValueError('The elements need to be a (n, 3)-vector.')

        # Transpose the elements matrix if rows and cols are mixed up
        if elements.shape[0] == 3:
            elements = elements.transpose()

        # Find the boundary
        boundary_indices: np.ndarray = cls.__find_boundary(elements)

        # Create the dual mesh
        dual_mesh = DualMesh.from_mesh(x, y, elements)

        # Create the edge mesh
        edge_mesh = EdgeMesh.from_mesh(x, y, elements, dual_mesh)

        # Compute areas
        areas = cls.__compute_areas(x, y, elements, dual_mesh,
                                    edge_mesh, boundary_indices)

        return Mesh(
            x=x,
            y=y,
            elements=elements,
            boundary_indices=boundary_indices,
            edge_mesh=edge_mesh,
            dual_mesh=dual_mesh,
            areas=areas,
            voltage_points=voltage_points,
            input_edge=input_edge,
            output_edge=output_edge
        )

    @classmethod
    def __find_boundary(cls, elements: np.ndarray) -> np.ndarray:
        """
        Find the boundary vertices.
        :param elements: The triangular elements.
        :return: A list of vertex indices corresponding to the boundary.
        """

        edges, is_boundary = get_edges(elements)

        # Get the boundary edges and all boundary points
        boundary_edges = edges[is_boundary.nonzero()[0], :]
        return np.unique(boundary_edges.flatten())

    @classmethod
    def __compute_areas(cls,
                        x: np.ndarray,
                        y: np.ndarray,
                        elements: np.ndarray,
                        dual_mesh: DualMesh,
                        edge_mesh: EdgeMesh,
                        boundary_indices: np.ndarray
                        ) -> np.ndarray:
        """
        Compute the area of the Voronoi region for each vertex.
        :param x:
        :return: A list of areas.
        """

        # Compute polygons to use when computing area
        polygons = get_surrounding_voronoi_polygons(elements, len(x))

        # Get the areas for each vertex
        return compute_surrounding_area(
            x=x,
            y=y,
            boundary=boundary_indices,
            edges=edge_mesh.edges,
            boundary_edge_indices=edge_mesh.boundary_edge_indices,
            x_dual=dual_mesh.x,
            y_dual=dual_mesh.y,
            polygons=polygons
        )

    def get_boundary(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the coordinates of the boundary vertices.
        :return: A tuple of the x and y coordinates for the boundary vertices.
        """
        return self.x[self.boundary_indices], self.y[self.boundary_indices]

    def get_boundary_index_where(self,
                                 *conditions: Callable[
                                     [np.ndarray, np.ndarray], Any
                                 ],
                                 operator: Operator = Operator.AND
                                 ) -> np.ndarray:
        """
        Get the indices for the boundary vertices that fulfill the conditions.
        :param conditions: A
        function (x: np.ndarray, y: np.ndarray) -> np.ndarray that takes
        the coordinates of the
        boundary vertices and returns a boolean array specifying which points
        to select. If multiple conditions are given the operator
        specifies how to merge the conditions.
        :param operator: Operator used to merge multiple conditions. The
        operator AND (np.all) gives the intersection and the
        operator OR (np.any) gives the union. Default is AND.
        :return: The selected boundary points.
        """
        return self.boundary_indices[operator([
            condition(*self.get_boundary()) for condition in conditions
        ], axis=0).nonzero()[0]]

    def get_edge_boundary_index_where(self,
                                      *conditions: Callable[
                                          [np.ndarray, np.ndarray], Any
                                      ],
                                      operator: Operator = Operator.AND
                                      ) -> np.ndarray:
        """
        Get the indices for the boundary edges that fulfill the conditions.
        :param conditions: A
        function (x: np.ndarray, y: np.ndarray) -> np.ndarray that takes
        the coordinates of the vertices in the boundary edges as a (n, 2)-vector
        and returns a boolean array specifying which points to select.
        If multiple conditions are given the operator specifies how to merge
        the conditions.
        :param operator: Operator used to merge multiple conditions. The
        operator AND (np.all) gives the intersection and the
        operator OR (np.any) gives the union. Default is AND.
        :return: The selected boundary points.
        """
        return operator([
            condition(
                self.x[self.edge_mesh.get_boundary_edges()],
                self.y[self.edge_mesh.get_boundary_edges()]
            )
            for condition in conditions
        ], axis=0).nonzero()[0]

    def get_mesh_index_where(self,
                             *conditions: Callable[
                                 [np.ndarray, np.ndarray], Any
                             ],
                             operator: Operator = Operator.AND
                             ) -> np.ndarray:
        """
        Get the indices for the mesh vertices that fulfill the conditions.
        :param conditions: A
        function (x: np.ndarray, y: np.ndarray) -> np.ndarray that takes
        the coordinates of the
        boundary vertices and returns a boolean array specifying which points
        to select. If multiple conditions are given the operator
        specifies how to merge the conditions.
        :param operator: Operator used to merge multiple conditions. The
        operator AND (np.all) gives the intersection and the
        operator OR (np.any) gives the union. Default is AND.
        :return: The selected boundary points.
        """
        return operator([
            condition(self.x, self.y) for condition in conditions
        ], axis=0).nonzero()[0]

    def get_flow_edges(self) -> Tuple[np.ndarray, np.ndarray]:
        input_edge = np.zeros_like(self.input_edge)

        # Make sure order is correct. Sometimes the order is not
        # correct in data files.
        input_edge[0] = np.minimum(self.input_edge[0], self.input_edge[1])
        input_edge[1] = np.maximum(self.input_edge[0], self.input_edge[1])
        input_edge[2] = np.minimum(self.input_edge[2], self.input_edge[3])
        input_edge[3] = np.maximum(self.input_edge[2], self.input_edge[3])

        output_edge = np.zeros_like(self.output_edge)

        # Make sure order is correct. Sometimes the order is not
        # correct in data files.
        output_edge[0] = np.minimum(self.output_edge[0], self.output_edge[1])
        output_edge[1] = np.maximum(self.output_edge[0], self.output_edge[1])
        output_edge[2] = np.minimum(self.output_edge[2], self.output_edge[3])
        output_edge[3] = np.maximum(self.output_edge[2], self.output_edge[3])

        return input_edge, output_edge

    def save_to_hdf5(self, h5group: h5py.Group):
        h5group['x'] = self.x
        h5group['y'] = self.y
        h5group['elements'] = self.elements
        h5group['boundary_indices'] = self.boundary_indices
        h5group['areas'] = self.areas
        h5group['voltage_points'] = self.voltage_points
        h5group['input_edge'] = self.input_edge
        h5group['output_edge'] = self.output_edge

        # Save the edge mesh
        self.edge_mesh.save_to_hdf5(h5group.create_group('edge_mesh'))

        # Save the dual mesh
        self.dual_mesh.save_to_hdf5(h5group.create_group('dual_mesh'))

    @classmethod
    def load_from_hdf5(cls, h5group: h5py.Group) -> 'Mesh':
        """
        Load mesh from HDF5 file.
        :param h5group: The HDF5 group to load the mesh from.
        :return: The loaded mesh.
        """

        # Check that the required attributes x, y, and elements are in the group
        if not ('x' in h5group and 'y' in h5group and 'elements' in h5group):
            raise IOError('Could not load mesh due to missing data.')

        # Check if the mesh can be restored
        if cls.is_restorable(h5group):

            # Restore the mesh with the data
            return Mesh(
                x=h5group['x'],
                y=h5group['y'],
                elements=h5group['elements'],
                boundary_indices=h5group['boundary_indices'],
                areas=h5group['areas'],
                dual_mesh=DualMesh.load_from_hdf5(h5group['dual_mesh']),
                edge_mesh=EdgeMesh.load_from_hdf5(h5group['edge_mesh']),
                voltage_points=np.asarray(h5group['voltage_points'])
                if 'voltage_points' in h5group else None,
                input_edge=np.asarray(h5group['input_edge'])
                if 'input_edge' in h5group else None,
                output_edge=np.asarray(h5group['output_edge'])
                if 'output_edge' in h5group else None
            )

        # Recreate mesh from triangulation data if not all data is available
        return Mesh.from_triangulation(
            x=np.asarray(h5group['x']).flatten(),
            y=np.asarray(h5group['y']).flatten(),
            elements=h5group['elements'],
            voltage_points=np.asarray(h5group['voltage_points'])
            if 'voltage_points' in h5group else None,
            input_edge=np.asarray(h5group['input_edge'])
            if 'input_edge' in h5group else None,
            output_edge=np.asarray(h5group['output_edge'])
            if 'output_edge' in h5group else None
        )

    @classmethod
    def is_restorable(cls, h5group: h5py.Group) -> bool:
        return 'x' in h5group and 'y' in h5group and 'elements' in h5group \
               and 'boundary_indices' in h5group and 'areas' in h5group \
               and 'edge_mesh' in h5group and 'dual_mesh' in h5group
