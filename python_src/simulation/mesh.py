""" Container class of mesh visualisation data """
from typing import Tuple, Union

import numpy as np
import plotly.graph_objects as go
from matplotlib.collections import LineCollection


class MeshData:
    """
        Drawing data for a mesh with vertex laytout 3f position 2f texture 3f normal
        Index data list of integer triplets for each triangle
        Texture data indicates where to use in each material in a render pass
    """
    def __init__(self, vertex_data: np.ndarray, index_data: np.ndarray, texture_data: dict):
        self._vertex_data = vertex_data
        self._index_data = index_data
        self._texture_data = texture_data

        self.place_at_origin()

    @property
    def nr_vertices(self) -> int:
        """ Get number of vertices """
        return len(self._vertex_data)

    @property
    def vertices_3d(self) -> np.ndarray:
        """ Reference to 3d vertices """
        return self._vertex_data[:, :3]

    @property
    def vertices_2d(self) -> np.ndarray:
        """ Reference to 2d vertices (x, y only) """
        return self._vertex_data[:, :2]

    def place_at_origin(self):
        """ Ensure object is stood upright (bottom at y=0) center x, z at 0, 0 """
        self._vertex_data[:, 0] -= self._vertex_data[:, 0].mean()
        self._vertex_data[:, 1] -= self._vertex_data[:, 1].min()
        self._vertex_data[:, 2] -= self._vertex_data[:, 2].mean()

    def scale_vertices(self, scalar: float):
        """ Scale vertices by a constant """
        self._vertex_data[:, :3] *= scalar

    def offset_vertices(self, offset: Union[Tuple[float, float, float], np.ndarray]):
        """ Update vertex locations in place by a fixed offset """
        self._vertex_data[:, :3] += offset

    def clamp_above_zero(self):
        """ Ensure vertices are always above 0 """
        self._vertex_data[:, :3] = np.maximum(self._vertex_data[:, :3], 0.)

    def create_plotly_mesh(self, **kwargs) -> go.Mesh3d:
        """ Create a plotly mesh for the mesh from vertex and index data """
        return go.Mesh3d(
            x=self._vertex_data[:, 0],
            y=self._vertex_data[:, 2],
            z=self._vertex_data[:, 1],  # Height is z axis in plot
            i=self._index_data[:, 0],
            j=self._index_data[:, 1],
            k=self._index_data[:, 2],
            flatshading=True,
            **kwargs
        )

    def create_line_collection(self, **kwargs) -> LineCollection:
        """ Create matplotlib line collection from a mesh """
        lines = []

        for face in self._index_data:
            lines.append([self._vertex_data[face[0]][:2], self._vertex_data[face[1]][:2]])
            lines.append([self._vertex_data[face[1]][:2], self._vertex_data[face[2]][:2]])
            lines.append([self._vertex_data[face[2]][:2], self._vertex_data[face[0]][:2]])

        return LineCollection(lines, **kwargs)

    def create_scatter_plot(self, **kwargs) -> go.Scatter3d:
        """ Create a scaltter plot from vertex locations """
        return go.Scatter3d(
            x=self._vertex_data[:, 0],
            y=self._vertex_data[:, 2],
            z=self._vertex_data[:, 1],
            mode='markers',
            **kwargs
        )
