""" Controller of a simulation run """
from typing import Dict
from time import perf_counter

from python_src.utils.read_obj import parse_obj
from python_src.utils.file_io import read_json
from python_src.simulation.mesh import MeshData
from python_src.simulation.piece_physics import DynamicPiece
from python_src.extract_clothing_vertex_data import extract_all_piece_vertices

from python_src.parameters import AVATAR_SCALING
NUMBER_STEPS = 10


class FabricSimulation:
    """ Run a fabric simulation """
    def __init__(self, body: MeshData, pieces: Dict[str, DynamicPiece]):
        self.body = body
        self.pieces = pieces
        self.frames = []
        self.add_vertices_to_frames()

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


if __name__ == '__main__':
    avatar_mesh = parse_obj('./assets/BodyMesh.obj')
    avatar_mesh.scale_vertices(AVATAR_SCALING)

    clothing_data = read_json('./assets/sewing_shirt.json')
    dynamic_pieces = extract_all_piece_vertices(clothing_data)

    simulation = FabricSimulation(avatar_mesh, dynamic_pieces)
    start = perf_counter()
    simulation.step(100)
    print(f'Time taken to run {NUMBER_STEPS} = {perf_counter() - start:.3}')
