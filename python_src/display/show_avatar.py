""" Display an .obj mesh data as a triangle surface """
from typing import List

import plotly.graph_objects as go
import numpy as np

from python_src.utils.read_obj import parse_obj
from python_src.utils.file_io import read_json
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices

from python_src.parameters import AVATAR_SCALING


def create_body_mesh(vertex_data: np.ndarray, index_data: np.ndarray,
                     color='lightblue', name='body') -> go.Mesh3d:
    """ Create a plotly mesh for the body from vertex and index data,
        first 3 columns of vertex data should be coordinates """
    return go.Mesh3d(
        x=vertex_data[:, 0] - vertex_data[:, 0].mean(),
        y=vertex_data[:, 2] - vertex_data[:, 2].mean(),
        z=vertex_data[:, 1] - vertex_data[:, 1].min(),  # Height is z axis
        i=index_data[:, 0],
        j=index_data[:, 1],
        k=index_data[:, 2],
        opacity=1.0,
        color=color,
        flatshading=True,
        name=name
    )


def show_meshes(meshes: List[go.Mesh3d]):
    """ Display plotly 3D meshes """
    fig = go.Figure(data=meshes)
    fig.update_layout(
        scene=dict(
                xaxis=dict(nticks=4, range=[-0.7, 0.7],),
                yaxis=dict(nticks=4, range=[-0.7, 0.7],),
                zaxis=dict(nticks=4, range=[0, 2])
            ),
        width=1200,
        margin=dict(r=20, l=10, b=10, t=10)
    )
    fig.show()


if __name__ == '__main__':
    vertex_data, index_data, _, _ = parse_obj('./assets/BodyMesh.obj')
    vertex_data[:, :3] *= AVATAR_SCALING
    mesh = create_body_mesh(vertex_data, index_data)

    clothing_data = read_json('./assets/sewing_shirt.json')
    clothing_display_data = extract_all_piece_vertices(clothing_data)
    vertex_data = clothing_display_data["L-1"]["vertex_data"] / 100.
    index_data = clothing_display_data["L-1"]["index_data"]
    front_panel_mesh = create_body_mesh(vertex_data, index_data, color='red', name="L-1")

    show_meshes([mesh, front_panel_mesh])
