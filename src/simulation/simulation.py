"""Controller that computes steps of a simulation"""

from typing import Dict
from time import perf_counter

from src.utils.read_obj import parse_obj
from src.utils.file_io import read_json
from src.simulation.mesh import MeshData
from src.simulation.dynamic_piece import DynamicPiece
from src.simulation.dynamic_clothing import DynamicClothing
from src.simulation.sewing_constraints import SewingConstraints
from src.simulation.setup.extract_clothing_vertex_data import extract_all_piece_vertices


from src.parameters import AVATAR_SCALING


class FabricSimulation:
    """Run a fabric simulation"""

    def __init__(
        self,
        body: MeshData,
        pieces: Dict[str, DynamicPiece],
        sewing_constraints: SewingConstraints,
    ):
        self.clothing = DynamicClothing(pieces, sewing_constraints, body)

    def step(self, nr_steps: int = 1):
        """Run simulation for a number of steps"""
        for step in range(nr_steps):
            self.clothing.update_forces(step)


if __name__ == "__main__":
    avatar_mesh = parse_obj("./assets/BodyMesh.obj", "./assets/BodyMesh.json")
    avatar_mesh.scale_vertices(AVATAR_SCALING)

    clothing_data = read_json("./assets/sewing_shirt.json")
    all_pieces, sewing_constraints = extract_all_piece_vertices(clothing_data)

    simulation = FabricSimulation(avatar_mesh, all_pieces, sewing_constraints)
    start = perf_counter()
    simulation.step(1)
    print(f"Time taken to run 1 piece {1} steps = {perf_counter() - start:.3}")
