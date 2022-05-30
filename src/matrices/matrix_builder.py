from enum import Enum, auto
from typing import Union, Sequence

import numpy as np
from scipy.sparse import csr_matrix

from src.matrices.build_divergence import build_divergence
from src.matrices.build_gradient import build_gradient
from src.mesh.mesh import Mesh
from src.matrices.build_laplacian import build_laplacian
from src.matrices.build_neumann_boundary_laplacian import build_neumann_boundary_laplacian
from src.sparse_format import SparseFormat


class MatrixType(Enum):
    LAPLACIAN = auto()
    NEUMANN_BOUNDARY_LAPLACIAN = auto()
    DIVERGENCE = auto()
    GRADIENT = auto()


class MatrixBuilder:

    def __init__(self, mesh: Mesh):
        """
        Create a matrix builder.
        :param mesh: The mesh to build matrices on.
        """
        self.mesh = mesh
        self.fixed_sites: Union[np.ndarray, None] = None
        self.fixed_sites_eigenvalue: float = 1
        self.link_exponents: Union[np.ndarray, None] = None

    def with_dirichlet_boundary(self, fixed_sites: Sequence[int],
                                fixed_sites_eigenvalues: float = 1
                                ) -> 'MatrixBuilder':
        """
        Add sites using Dirichlet boundary condition.
        :param fixed_sites: The sites using Dirichlet boundary condition.
        :param fixed_sites_eigenvalues: The eigenvalues when applying the
        matrix on one of these sites.
        :return: This builder.
        """
        self.fixed_sites = np.asarray(fixed_sites)
        self.fixed_sites_eigenvalue = fixed_sites_eigenvalues
        return self

    def with_link_exponents(self,
                            link_exponents: Sequence[float]
                            ) -> 'MatrixBuilder':
        """
        Add link exponents to the matrix.
        :param link_exponents: The value is integrated, exponentiated and
        used as a link variable.
        :return: This builder.
        """
        self.link_exponents = np.asarray(link_exponents)
        return self

    def build(self,
              matrix_type: MatrixType,
              sparse_format: SparseFormat = SparseFormat.CSR
              ) -> csr_matrix:
        """
        Build a matrix.
        :param matrix_type: The type of matrix to build.
        :param sparse_format: The matrix format to return.
        :return: The matrix
        """

        if matrix_type is MatrixType.LAPLACIAN:
            return build_laplacian(self.mesh,
                                   self.link_exponents,
                                   self.fixed_sites,
                                   self.fixed_sites_eigenvalue,
                                   sparse_format)

        if matrix_type is MatrixType.NEUMANN_BOUNDARY_LAPLACIAN:
            return build_neumann_boundary_laplacian(self.mesh, self.fixed_sites)

        if matrix_type is MatrixType.DIVERGENCE:
            return build_divergence(self.mesh)

        if matrix_type is MatrixType.GRADIENT:
            return build_gradient(self.mesh, self.link_exponents)

        raise ValueError('Unknown matrix type.')

    def clone(self) -> 'MatrixBuilder':
        """
        Make a copy of the matrix builder.
        :return: A copy of the matrix builder
        """

        clone = MatrixBuilder(self.mesh)
        clone.fixed_sites = np.copy(self.fixed_sites)
        clone.fixed_sites_eigenvalue = self.fixed_sites_eigenvalue
        clone.link_exponents = np.copy(self.link_exponents)
        return clone
