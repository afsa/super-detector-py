import numpy as np

from src.mesh.mesh import Mesh


class BoundingBox:
    """
    A bounding box for the mesh.
    """

    def __init__(self, mesh: Mesh):

        self.min_x = np.min(mesh.x)
        self.max_x = np.max(mesh.x)

        self.min_y = np.min(mesh.y)
        self.max_y = np.max(mesh.y)
