import numpy as np


def get_dual_edge_lengths(xe: np.ndarray,
                          ye: np.ndarray,
                          elements: np.ndarray,
                          x_dual: np.ndarray,
                          y_dual: np.ndarray,
                          edges: np.ndarray
                          ) -> np.ndarray:
    """
    Compute the lengths of the dual edges.
    :param xe: The x coordinates for the edges.
    :param ye: The y coordinates for the edges.
    :param elements: The triangular elements in the tesselation.
    :param x_dual: The x coordinates for the dual mesh (Voronoi sites).
    :param y_dual: The y coordinates for the dual mesh (Voronoi sites).
    :param edges: The edges connecting the sites.
    :return: An array of dual edge lengths.
    """

    # Create a dict with keys corresponding to the edges and values
    # corresponding to the triangles
    edge_to_element = {}

    # Iterate over all elements to create the edge_to_element dict
    edge_element_indices = [[0, 1], [1, 2], [2, 0]]
    for i, element in enumerate(elements):

        for idx in edge_element_indices:

            # Hash the array by converting it to a string
            edge = str(np.sort(element[idx]))

            if edge in edge_to_element:
                edge_to_element[edge].append(i)
            else:
                edge_to_element[edge] = [i]

    dual_lengths = np.zeros_like(xe)

    # Iterate over all edges
    for i, edge in enumerate(edges):

        # Get the elements from the dict
        indices = edge_to_element[str(edge)]

        # Handle boundary edges
        if len(indices) == 1:
            dual_lengths[i] = np.sqrt((x_dual[indices[0]] - xe[i]) ** 2
                                      + (y_dual[indices[0]] - ye[i]) ** 2)

        # Handle inner edges
        else:
            dual_lengths[i] = np.sqrt(
                (x_dual[indices[0]] - x_dual[indices[1]]) ** 2
                + (y_dual[indices[0]] - y_dual[indices[1]]) ** 2
            )

    return dual_lengths
