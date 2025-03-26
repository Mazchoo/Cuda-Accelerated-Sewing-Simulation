""" Display an .obj mesh data as a triangle surface """
from typing import List

import plotly.graph_objects as go
import numpy as np

from python_src.utils.read_obj import parse_obj


def create_body_mesh(vertex_data: np.ndarray, index_data: np.ndarray,
                     color='lightblue') -> go.Mesh3d:
    """ Create a plotly mesh for the body from vertex and index data,
        first 3 columns of vertex data should be coordinates """
    return go.Mesh3d(
        x=vertex_data[:, 0],
        y=vertex_data[:, 2],
        z=vertex_data[:, 1] - vertex_data[:, 1].min(),  # Height is z axis
        i=index_data[:, 0],
        j=index_data[:, 1],
        k=index_data[:, 2],
        opacity=0.5,
        color=color
    )


def show_meshes(meshes: List[go.Mesh3d]):
    """ Display plotly 3D meshes """
    fig = go.Figure(data=meshes)
    fig.update_layout(
        scene=dict(
            xaxis=dict(nticks=4, range=[-1, 1],),
            yaxis=dict(nticks=4, range=[-1, 1],),
            zaxis=dict(nticks=4, range=[0, 3.2])),
        width=1200,
        margin=dict(r=20, l=10, b=10, t=10)
    )
    fig.show()


if __name__ == '__main__':
    vertex_data, index_data, _, _ = parse_obj('./assets/BodyMesh.obj')
    mesh = create_body_mesh(vertex_data, index_data)
    show_meshes([mesh])
