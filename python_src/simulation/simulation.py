""" Controller of a simulation run """
from typing import Dict
from time import perf_counter

import plotly.graph_objects as go

from python_src.display.common import get_hsv_colors, float_rgb_to_str
from python_src.simulation.Geometry import Geometry
from python_src.utils.read_obj import parse_obj
from python_src.utils.file_io import read_json
from python_src.simulation.mesh import MeshData
from python_src.simulation.piece_physics import DynamicPiece
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices


from python_src.parameters import AVATAR_SCALING
NUMBER_STEPS = 10


class FabricSimulation:
    """ Run a fabric simulation and keep track of piece positions """
    def __init__(self, body: Geometry, pieces: Dict[str, DynamicPiece]):
        self.body = body
        self.pieces = pieces
        self.frames = []
        self.add_vertices_to_frames()

        self.body_scatter_plot = self.body.create_scatter_plot(marker=dict(color='grey', size=6),
                                                               name='Body')
        self.colors = [float_rgb_to_str(c) for c in get_hsv_colors(len(self.pieces))]

    def add_vertices_to_frames(self):
        """ Update stored positions in animation buffer """
        self.frames.append({k: piece.mesh.vertices_3d.copy() for k, piece in self.pieces.items()})

    def step(self, nr_steps: int = 1):
        ''' Run simulation for one time step '''
        for _ in range(nr_steps):
            for piece in self.pieces.values():
                piece.update_forces()

            # ToDo - bend forces
            # ToDo - sewing forces
            # ToDo - body collision

            for piece in self.pieces.values():
                piece.update_velocities()
                piece.update_positions()

            self.add_vertices_to_frames()

    @property
    def nr_frames(self) -> int:
        """ Get total number of frames to display """
        return len(self.frames)

    def get_scatter_at_frame(self, i: int) -> go.Frame:
        """ Return snapshot of simulation as series of scatter plots """
        data = [self.body_scatter_plot]
        frame_positions = self.frames[i]

        for j, (piece_name, vertices_3d) in enumerate(frame_positions.items()):
            data.append(go.Scatter3d(
                x=vertices_3d[:, 0],
                y=vertices_3d[:, 2],
                z=vertices_3d[:, 1],
                mode='markers',
                marker=dict(color=self.colors[j], size=6),
                name=piece_name
            ))

        return go.Frame(
            data=data,
            name=str(i)
        )


if __name__ == '__main__':
    avatar_mesh = parse_obj('./assets/BodyMesh.obj')
    geo_avatar = Geometry(avatar_mesh)
    geo_avatar.Scale(AVATAR_SCALING)

    clothing_data = read_json('./assets/sewing_shirt.json')
    all_pieces = extract_all_piece_vertices(clothing_data)
    one_piece_dict = {"L1": all_pieces["L-1"]}

    simulation = FabricSimulation(geo_avatar, one_piece_dict)
    start = perf_counter()
    simulation.step(100)
    print(f'Time taken to run {NUMBER_STEPS} = {perf_counter() - start:.3}')
