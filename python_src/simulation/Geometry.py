from typing import List, Union
from matplotlib.collections import LineCollection
import plotly.graph_objects as go

import numpy as np
from python_src.simulation.mesh import MeshData


class Geometry:
    def __init__(self, mesh: MeshData, color: str = "gray", opacity: float = 1.0):
        self.mesh = mesh
        self.color = color
        self.opacity = opacity
        self.Centering()
    
    @property
    def nr_vertices(self) -> int:
        """Get the number of vertices from the mesh."""
        return self.mesh.nr_vertices  # Access the property from the MeshData instance
    
    
    @property
    def vertices_3d(self) -> np.ndarray:
        """ Reference to 3d vertices """
        return self.mesh._vertex_data[:, :3]
    
    @property
    def vertices_2d(self) -> np.ndarray:
        """ Reference to 2d vertices (x, y only) """
        return self.mesh._vertex_data[:, :2]


    def Centering(self):
        self.mesh.vertex_data[:, 0] -= self.mesh.vertex_data[:, 0].mean()
        self.mesh.vertex_data[:, 1] -= self.mesh.vertex_data[:, 1].min()
        self.mesh.vertex_data[:, 2] -= self.mesh.vertex_data[:, 2].mean()

    def Scale(self, scalar: float):
        self.mesh.vertex_data[:, :3] *= scalar

    def Translate(self, offset: Union[tuple[float, float, float], np.ndarray]):
        self.mesh.vertex_data[:, :3] += offset

    def rotate(self, angle_degrees: float, axis: Union[np.ndarray, List[int]]):
        angle_radians = np.radians(angle_degrees)
        axis = np.array(axis)
        axis = axis / np.linalg.norm(axis)

        cos_angle = np.cos(angle_radians)
        sin_angle = np.sin(angle_radians)
        one_minus_cos = 1 - cos_angle

        rotation_matrix = np.array([
            [cos_angle + axis[0]**2 * one_minus_cos,
             axis[0] * axis[1] * one_minus_cos - axis[2] * sin_angle,
             axis[0] * axis[2] * one_minus_cos + axis[1] * sin_angle],

            [axis[1] * axis[0] * one_minus_cos + axis[2] * sin_angle,
             cos_angle + axis[1]**2 * one_minus_cos,
             axis[1] * axis[2] * one_minus_cos - axis[0] * sin_angle],

            [axis[2] * axis[0] * one_minus_cos - axis[1] * sin_angle,
             axis[2] * axis[1] * one_minus_cos + axis[0] * sin_angle,
             cos_angle + axis[2]**2 * one_minus_cos]
        ])

        self.mesh.vertex_data[:, :3] = self.mesh.vertex_data[:, :3] @ rotation_matrix.T

    def clamp_above_zero(self):
        self.mesh.vertex_data[:, 1] = np.maximum(self.mesh.vertex_data[:, 1], 0.)

    def create_plotly_mesh(self) -> go.Mesh3d:
        v = self.mesh.vertex_data
        i = self.mesh.index_data
        return go.Mesh3d(
            x=v[:, 0],
            y=v[:, 2],
            z=v[:, 1],
            i=i[:, 0],
            j=i[:, 1],
            k=i[:, 2],
            flatshading=True,
            color=self.color,
            opacity=self.opacity
        )

    def create_line_collection(self, **kwargs) -> LineCollection:
        lines = []
        for face in self.mesh.index_data:
            lines.append([self.mesh.vertex_data[face[0]][:2], self.mesh.vertex_data[face[1]][:2]])
            lines.append([self.mesh.vertex_data[face[1]][:2], self.mesh.vertex_data[face[2]][:2]])
            lines.append([self.mesh.vertex_data[face[2]][:2], self.mesh.vertex_data[face[0]][:2]])
        return LineCollection(lines, **kwargs)

    def create_scatter_plot(self, **kwargs) -> go.Scatter3d:
        v = self.mesh.vertex_data
        return go.Scatter3d(
            x=v[:, 0],
            y=v[:, 2],
            z=v[:, 1],
            mode='markers',
            marker=dict(color=self.color),
            **kwargs
        )
