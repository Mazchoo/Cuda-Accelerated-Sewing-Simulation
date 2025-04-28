""" Controller of a simulation run """
from typing import Dict
from time import perf_counter

import plotly.graph_objects as go

from src.display.common import get_hsv_colors, float_rgb_to_str
from src.utils.read_obj import parse_obj
from src.utils.file_io import read_json
from src.simulation.mesh import MeshData, create_mesh_scatter_plot
from src.simulation.piece_physics import DynamicPiece
from src.simulation.sewing_forces import SewingForces
from src.simulation.setup.extract_clothing_vertex_data import extract_all_piece_vertices


from src.parameters import AVATAR_SCALING, NR_STEPS, RUN_COLLISION_DETECTION


class FabricSimulation:
    """ Run a fabric simulation and keep track of piece positions """
    def __init__(self, body: MeshData, pieces: Dict[str, DynamicPiece], sewing_forces: SewingForces):
        self.body = body
        self.pieces = pieces
        self.sewing_forces = sewing_forces

        self.frames = []
        self.add_vertices_to_frames()

        self.body_scatter_plot = create_mesh_scatter_plot(self.body, marker=dict(color='grey', size=6),
                                                          name='Body')
        self.colors = [float_rgb_to_str(c) for c in get_hsv_colors(len(self.pieces))]

    def add_vertices_to_frames(self):
        """ Update stored positions in animation buffer """
        self.frames.append({k: piece.mesh.vertices_3d.copy() for k, piece in self.pieces.items()})

    def step(self, nr_steps: int = 1):
        ''' Run simulation for one time step '''
        for step in range(nr_steps):
            for piece in self.pieces.values():
                piece.update_internal_forces()

            for piece in self.pieces.values():
                piece.update_velocities(step)
                piece.update_positions()
                if RUN_COLLISION_DETECTION:
                    piece.body_collision_adjustment(self.body.trimesh)

            self.sewing_forces.recalculate_adjustment(self.pieces)
            for piece_key, piece in self.pieces.items():
                adjustment = self.sewing_forces.get_adjustment_for_piece(piece_key)
                piece.apply_adjustment(adjustment)

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
    avatar_mesh = parse_obj('./assets/BodyMesh.obj', './assets/BodyAnnotations.json')
    avatar_mesh.scale_vertices(AVATAR_SCALING)

    clothing_data = read_json('./assets/sewing_shirt.json')
    all_pieces, sewing_forces = extract_all_piece_vertices(clothing_data)
    one_piece_dict = {"L1": all_pieces["L-1"]}

    simulation = FabricSimulation(avatar_mesh, one_piece_dict, sewing_forces)
    start = perf_counter()
    simulation.step(100)
    print(f'Time taken to run 1 piece {NR_STEPS} steps = {perf_counter() - start:.3}')
