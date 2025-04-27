""" Display functions for sewing lines on meshes """
from typing import Dict

import plotly.graph_objects as go

from python_src.simulation.sewing_forces import SewingForces
from python_src.simulation.piece_physics import DynamicPiece
from python_src.display.common import get_hsv_colors, float_rgb_to_str


def add_sewing_points_to_plotly_fig(pieces: Dict[str, DynamicPiece], sewing: SewingForces,
                                    fig: go.Figure, **kwargs):
    """ Add annotations as text to figure """
    colors = get_hsv_colors(len(sewing) + 1)

    for i, sewing_pair in enumerate(sewing):
        xs, ys, zs = [], [], []

        from_piece_vertices = pieces[sewing_pair.from_piece].mesh.vertices_3d
        from_vertices = from_piece_vertices[sewing_pair.indices[:, 0]]
        for x, y, z in from_vertices:
            xs.append(x)
            ys.append(y)
            zs.append(z)

        to_piece_vertices = pieces[sewing_pair.to_piece].mesh.vertices_3d
        to_vertices = to_piece_vertices[sewing_pair.indices[:, 1]]
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
