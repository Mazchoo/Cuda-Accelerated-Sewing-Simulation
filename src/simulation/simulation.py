"""Controller of a simulation run"""

from typing import Dict
from time import perf_counter

import plotly.graph_objects as go

from src.display.common import get_hsv_colors, float_rgb_to_str
from src.utils.read_obj import parse_obj
from src.utils.file_io import read_json
from src.simulation.mesh import MeshData, create_mesh_scatter_plot
from src.simulation.dynamic_piece import DynamicPiece
from src.simulation.dynamic_clothing import DynamicClothing
from src.simulation.sewing_constraints import SewingConstraints
from src.simulation.setup.extract_clothing_vertex_data import extract_all_piece_vertices


from src.parameters import AVATAR_SCALING


class FabricSimulation:
    """Run a fabric simulation and keep track of piece positions"""

    def __init__(
        self,
        body: MeshData,
        pieces: Dict[str, DynamicPiece],
        sewing_constraints: SewingConstraints,
    ):
        self.clothing = DynamicClothing(pieces, sewing_constraints, body)

        self.frames = []
        self.add_vertices_to_frames()

        self.body_scatter_plot = create_mesh_scatter_plot(
            body, marker=dict(color="grey", size=6), name="Body"
        )
        self.colors = [float_rgb_to_str(c) for c in get_hsv_colors(len(pieces))]

    def add_vertices_to_frames(self):
        """Update stored positions in animation buffer"""
        self.frames.append(self.clothing.vertices_3d.copy())

    def step(self, nr_steps: int = 1, logging: bool = True):
        """Run simulation for a number of steps"""
        for step in range(nr_steps):
            self.clothing.update_forces(step)

            self.add_vertices_to_frames()
            if logging:
                print(f"Running step {step + 1}/{nr_steps}")

    @property
    def nr_frames(self) -> int:
        """Get total number of frames to display"""
        return len(self.frames)

    def get_scatter_at_frame(self, i: int) -> go.Frame:
        """Return snapshot of simulation as series of scatter plots"""
        data = [self.body_scatter_plot]
        vertices = self.frames[i]

        for j, (piece_name, (start_ind, end_ind)) in enumerate(
            self.clothing.piece_to_index_range.items()
        ):
            data.append(
                go.Scatter3d(
                    x=vertices[start_ind:end_ind, 0],
                    y=vertices[start_ind:end_ind, 2],
                    z=vertices[start_ind:end_ind, 1],
                    mode="markers",
                    marker=dict(color=self.colors[j], size=6),
                    name=piece_name,
                )
            )

        return go.Frame(data=data, name=str(i))


if __name__ == "__main__":
    avatar_mesh = parse_obj("./assets/BodyMesh.obj", "./assets/BodyAnnotations.json")
    avatar_mesh.scale_vertices(AVATAR_SCALING)

    clothing_data = read_json("./assets/sewing_shirt.json")
    all_pieces, sewing_constraints = extract_all_piece_vertices(clothing_data)

    simulation = FabricSimulation(avatar_mesh, all_pieces, sewing_constraints)
    start = perf_counter()
    simulation.step(1)
    print(f"Time taken to run 1 piece {1} steps = {perf_counter() - start:.3}")
