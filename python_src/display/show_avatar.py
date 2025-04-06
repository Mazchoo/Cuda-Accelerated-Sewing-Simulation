""" Display an .obj mesh data as a triangle surface """
from typing import List

import plotly.graph_objects as go

from python_src.simulation.Geometry import Geometry
from python_src.utils.read_obj import parse_obj
from python_src.utils.file_io import read_json
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices

from python_src.parameters import AVATAR_SCALING


def show_meshes(meshes: List[go.Mesh3d]):
    """ Display plotly 3D meshes """
    fig = go.Figure(data=meshes)
    fig.update_layout(
        scene=dict(
                xaxis=dict(nticks=20, range=[-0.7, 0.7],),
                yaxis=dict(nticks=20, range=[-0.7, 0.7],),
                zaxis=dict(nticks=20    , range=[0, 2])
            ),
        width=1200,
        margin=dict(r=20, l=10, b=10, t=10)
    )
    fig.show()


if __name__ == '__main__':
    avatar_mesh = parse_obj('./assets/BodyMesh.obj')
    geo_avatar = Geometry(avatar_mesh)
    geo_avatar.Scale(AVATAR_SCALING)
    geo_avatar.Translate([0, 0, 0])
    avatar_plotly = geo_avatar.create_plotly_mesh()
    
    clothing_data = read_json('./assets/sewing_shirt.json')
    clothing_display_data = extract_all_piece_vertices(clothing_data)

    front_panel_mesh = clothing_display_data["L-1"].mesh

    geo_front_panel = Geometry(mesh=front_panel_mesh, color='red', opacity=0.8)


    geo_front_panel.Translate([0, 0.8, 0.2])
    front_panel_plotly = front_panel_mesh.create_plotly_mesh()

    back_panel_mesh = clothing_display_data["L-2"].mesh
    geo_back_panel = Geometry(mesh=back_panel_mesh, color='red', opacity=0.8)

    geo_back_panel.Translate([0, 0.8, -0.2])
    back_panel_plotly = geo_back_panel.create_plotly_mesh()

    show_meshes([avatar_plotly, front_panel_plotly, back_panel_plotly])
