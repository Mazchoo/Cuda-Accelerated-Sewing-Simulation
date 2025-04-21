""" Display an .obj mesh data as a triangle surface """
from typing import List

import plotly.graph_objects as go

from python_src.utils.read_obj import parse_obj
from python_src.utils.file_io import read_json
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices
from python_src.simulation.mesh import MeshData, create_plotly_mesh, add_annotations_to_plotly_fig

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


def show_meshes_with_annotations(plotly_meshes: List[go.Mesh3d],
                                 annotation_meshes: List[MeshData],
                                 **annotation_kwargs):
    """ Display plotly 3D meshes with annotated points """
    fig = go.Figure(data=plotly_meshes)
    for mesh in annotation_meshes:
        add_annotations_to_plotly_fig(mesh, fig, **annotation_kwargs)

    fig.update_layout(
        scene=dict(
                xaxis=dict(nticks=4, range=[-2, 2],),
                yaxis=dict(nticks=4, range=[-2, 2],),
                zaxis=dict(nticks=4, range=[-2, 4])
            ),
        width=1200,
        margin=dict(r=20, l=10, b=10, t=10)
    )
    fig.show()


if __name__ == '__main__':
    avatar_mesh = parse_obj('./assets/BodyMesh.obj', './assets/BodyAnnotations.json')
    avatar_mesh.scale_vertices(AVATAR_SCALING)
    avatar_plotly = create_plotly_mesh(avatar_mesh, color='lightblue', name='avatar', opacity=1.0)

    clothing_data = read_json('./assets/sewing_shirt.json')
    clothing_display_data = extract_all_piece_vertices(clothing_data, avatar_mesh)

    front_panel_mesh = clothing_display_data["L-1"].mesh
    front_panel_plotly = create_plotly_mesh(front_panel_mesh, color='red', name="L-1", opacity=0.8)

    back_panel_mesh = clothing_display_data["L-2"].mesh
    back_panel_plotly = create_plotly_mesh(back_panel_mesh, color='green', name="L-2", opacity=0.8)

    sleeve_right_mesh = clothing_display_data["L-3"].mesh
    sleeve_right_plotly = create_plotly_mesh(sleeve_right_mesh, color='blue', name="L-3", opacity=0.8)

    sleeve_left_mesh = clothing_display_data["L-3-flip"].mesh
    sleeve_left_plotly = create_plotly_mesh(sleeve_left_mesh, color='yellow', name="L-3-flip", opacity=0.8)

    show_meshes_with_annotations([avatar_plotly, front_panel_plotly,
                                  back_panel_plotly, sleeve_right_plotly, sleeve_left_plotly],
                                 [avatar_mesh],
                                 marker=dict(size=4, color='black'),
                                 textfont=dict(size=14, color='black'))
