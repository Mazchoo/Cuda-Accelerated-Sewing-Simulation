""" Display an .obj mesh data as a triangle surface """
from typing import List, Dict

import plotly.graph_objects as go

from src.utils.read_obj import parse_obj
from src.utils.file_io import read_json
from src.simulation.setup.extract_clothing_vertex_data import extract_all_piece_vertices

from src.simulation.mesh import MeshData, create_plotly_mesh, add_annotations_to_plotly_fig
from src.simulation.piece_physics import DynamicPiece
from src.simulation.sewing_forces import SewingForces
from src.display.show_sewing import add_sewing_points_to_plotly_fig

from src.parameters import AVATAR_SCALING


def show_meshes(meshes: List[go.Mesh3d]):
    """ Display plotly 3D meshes """
    fig = go.Figure(data=meshes)
    fig.update_layout(
        scene=dict(
                xaxis=dict(nticks=4, range=[-1, 1],),
                yaxis=dict(nticks=4, range=[-1, 1],),
                zaxis=dict(nticks=4, range=[0, 2]),
                aspectmode='cube',
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
                xaxis=dict(nticks=4, range=[-1, 1],),
                yaxis=dict(nticks=4, range=[-1, 1],),
                zaxis=dict(nticks=4, range=[0, 2]),
                aspectmode='cube',
            ),
        width=1200,
        margin=dict(r=20, l=10, b=10, t=10)
    )
    fig.show()


def show_meshes_with_sewing_points(plotly_meshes: List[go.Mesh3d],
                                   dynamic_pieces: Dict[str, DynamicPiece],
                                   sewing: SewingForces):
    """ Display plotly 3D meshes with annotated points """
    fig = go.Figure(data=plotly_meshes)
    add_sewing_points_to_plotly_fig(dynamic_pieces, sewing, fig)

    fig.update_layout(
        scene=dict(
                xaxis=dict(nticks=4, range=[-1, 1],),
                yaxis=dict(nticks=4, range=[-1, 1],),
                zaxis=dict(nticks=4, range=[0, 2.5]),
                aspectmode='cube',
            ),
        width=1200,
        margin=dict(r=20, l=10, b=10, t=10)
    )
    fig.show()
    return fig


def show_each_mesh_different_colors(avatar_mesh: MeshData,
                                    dynamic_pieces: Dict[str, DynamicPiece],
                                    sewing_forces: SewingForces):
    avatar_plotly = create_plotly_mesh(avatar_mesh, color='lightblue', name='avatar', opacity=1.0)

    front_panel_mesh = dynamic_pieces["L-1"].mesh
    front_panel_plotly = create_plotly_mesh(front_panel_mesh, color='red', name="L-1", opacity=0.8)

    back_panel_mesh = dynamic_pieces["L-2"].mesh
    back_panel_plotly = create_plotly_mesh(back_panel_mesh, color='green', name="L-2", opacity=0.8)

    sleeve_right_mesh = dynamic_pieces["L-3"].mesh
    sleeve_right_plotly = create_plotly_mesh(sleeve_right_mesh, color='blue', name="L-3", opacity=0.8)

    sleeve_left_mesh = dynamic_pieces["L-3-flip"].mesh
    sleeve_left_plotly = create_plotly_mesh(sleeve_left_mesh, color='yellow', name="L-3-flip", opacity=0.8)

    return show_meshes_with_sewing_points([avatar_plotly, front_panel_plotly,
                                           back_panel_plotly, sleeve_right_plotly, sleeve_left_plotly],
                                          dynamic_pieces, sewing_forces)


if __name__ == '__main__':
    avatar_mesh = parse_obj('./assets/BodyMesh.obj', './assets/BodyAnnotations.json')
    avatar_mesh.scale_vertices(AVATAR_SCALING)

    clothing_data = read_json('./assets/sewing_shirt.json')
    dynamic_pieces, sewing_forces = extract_all_piece_vertices(clothing_data, avatar_mesh)

    show_each_mesh_different_colors(avatar_mesh, dynamic_pieces, sewing_forces)
