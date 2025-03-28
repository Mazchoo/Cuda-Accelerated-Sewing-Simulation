""" Controller of a simulation run """
from typing import Dict

from python_src.simulation.mesh import MeshData
from python_src.simulation.piece_physics import DynamicPiece


class FabricSimulation:
    """ Run a fabric simulation """
    def __init__(self, body: MeshData, pieces: Dict[str, DynamicPiece]):
        self.body = body
        self.pieces = pieces

    def step(self):
        ''' Run simulation for one time step '''
        for piece in self.pieces.values():
            piece.update_forces()

        # ToDo - tensile forces
        # ToDo - sewing forces
        # ToDo - body collision

        for piece in self.pieces.values():
            piece.update_velocities()
            piece.update_positions()
