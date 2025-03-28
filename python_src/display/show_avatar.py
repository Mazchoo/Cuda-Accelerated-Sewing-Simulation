""" Display an .obj mesh data as a triangle surface """
from typing import List

import plotly.graph_objects as go

from python_src.utils.read_obj import parse_obj
from python_src.utils.file_io import read_json
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices

from python_src.parameters import AVATAR_SCALING


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
    avatar_mesh = parse_obj('./assets/BodyMesh.obj')
    avatar_mesh.place_at_origin()
    avatar_mesh.scale_vertices(AVATAR_SCALING)
    avatar_plotly = avatar_mesh.create_plotly_mesh(color='lightblue', name='avatar', opacity=1.0)

    clothing_data = read_json('./assets/sewing_shirt.json')
    clothing_display_data = extract_all_piece_vertices(clothing_data)

    front_panel_mesh = clothing_display_data["L-1"].mesh
    front_panel_mesh.place_at_origin()
    front_panel_mesh.offset_vertices([0, 0.8, 0.2])
    front_panel_plotly = front_panel_mesh.create_plotly_mesh(color='red', name="L-1", opacity=0.8)

    back_panel_mesh = clothing_display_data["L-2"].mesh
    front_panel_mesh.place_at_origin()
    back_panel_mesh.offset_vertices([0, 0.8, -0.2])
    back_panel_plotly = back_panel_mesh.create_plotly_mesh(color='green', name="L-2", opacity=0.8)

    show_meshes([avatar_plotly, front_panel_plotly, back_panel_plotly])
