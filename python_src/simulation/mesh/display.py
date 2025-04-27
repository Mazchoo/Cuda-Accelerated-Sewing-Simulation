""" Dispatch to convert mesh into different display objects """
import plotly.graph_objects as go
from matplotlib.collections import LineCollection

from python_src.simulation.mesh import MeshData


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
