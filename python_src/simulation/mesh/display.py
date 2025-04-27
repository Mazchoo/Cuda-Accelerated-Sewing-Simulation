""" Dispatch to convert mesh into different display objects """
from typing import Dict

import plotly.graph_objects as go
from matplotlib.collections import LineCollection

from python_src.simulation.mesh import MeshData
from python_src.simulation.sewing_forces import SewingForces
from python_src.simulation.piece_physics import DynamicPiece
from python_src.display.common import get_hsv_colors, float_rgb_to_str


def create_plotly_mesh(mesh: MeshData, **kwargs) -> go.Mesh3d:
    """ Create a plotly mesh for the mesh from vertex and index data """
    return go.Mesh3d(
        x=mesh._vertex_data[:, 0],
        y=mesh._vertex_data[:, 2],
        z=mesh._vertex_data[:, 1],  # Height is z axis in plot
        i=mesh._index_data[:, 0],
        j=mesh._index_data[:, 1],
        k=mesh._index_data[:, 2],
        flatshading=True,
        **kwargs
    )


def create_mesh_line_collection(mesh: MeshData, **kwargs) -> LineCollection:
    """ Create matplotlib line collection from a mesh """
    lines = []

    for face in mesh._index_data:
        lines.append([mesh._vertex_data[face[0]][:2], mesh._vertex_data[face[1]][:2]])
        lines.append([mesh._vertex_data[face[1]][:2], mesh._vertex_data[face[2]][:2]])
        lines.append([mesh._vertex_data[face[2]][:2], mesh._vertex_data[face[0]][:2]])

    return LineCollection(lines, **kwargs)


def create_mesh_scatter_plot(mesh: MeshData, **kwargs) -> go.Scatter3d:
    """ Create a scaltter plot from vertex locations """
    return go.Scatter3d(
        x=mesh._vertex_data[:, 0],
        y=mesh._vertex_data[:, 2],
        z=mesh._vertex_data[:, 1],
        mode='markers',
        **kwargs
    )


def add_annotations_to_plotly_fig(mesh: MeshData, fig: go.Figure, **kwargs):
    """ Add annotations as text to figure """
    labels, xs, ys, zs = [], [], [], []
    for name, (x, y, z) in mesh.annotations.items():
        labels.append(name)
        xs.append(x)
        ys.append(y)
        zs.append(z)

    fig.add_trace(go.Scatter3d(
        x=xs, y=zs, z=ys,
        mode='markers+text',
        text=labels,
        **kwargs
    ))


def add_sewing_points_to_plotly_fig(pieces: Dict[str, DynamicPiece], sewing: SewingForces,
                                    fig: go.Figure, **kwargs):
    """ Add annotations as text to figure """
    colors = get_hsv_colors(len(sewing) + 1)

    for i, sewing_pair in enumerate(sewing):
        xs, ys, zs = [], [], []

        from_piece_vertices = pieces[sewing_pair.from_piece].mesh.vertices_3d
        from_vertices = from_piece_vertices[sewing_pair.from_indices]
        for x, y, z in from_vertices:
            xs.append(x)
            ys.append(y)
            zs.append(z)

        to_piece_vertices = pieces[sewing_pair.to_piece].mesh.vertices_3d
        to_vertices = to_piece_vertices[sewing_pair.to_indices]
        for x, y, z in to_vertices:
            xs.append(x)
            ys.append(y)
            zs.append(z)

        fig.add_trace(go.Scatter3d(
            x=xs, y=zs, z=ys,
            mode='markers',
            name=f"sewing {i}",
            marker=dict(
                color=float_rgb_to_str(colors[i])
            ),
            **kwargs
        ))
