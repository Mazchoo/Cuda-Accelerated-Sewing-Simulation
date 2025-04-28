""" Container class of mesh visualisation data """
from typing import Tuple, Union, Optional

import numpy as np
from trimesh import Trimesh


class MeshData:
    """
        Drawing data for a mesh with vertex laytout 3f position 2f texture 3f normal
        Index data list of integer triplets for each triangle
        Texture data indicates where to use in each material in a render pass
    """
    def __init__(self, vertex_data: np.ndarray, index_data: np.ndarray, texture_data: dict,
                 annotations: Optional[dict] = None, turn_points: Optional[np.ndarray] = None):
        self._vertex_data = vertex_data
        self._index_data = index_data
        self._texture_data = texture_data

        self._trimesh = None
        self._annotations = annotations if annotations is not None else {}
        self._turn_points = turn_points

        self.origin_array = self.place_at_origin()

    @property
    def nr_vertices(self) -> int:
        """ Get number of vertices """
        return len(self._vertex_data)

    @property
    def nr_turn_points(self) -> int:
        """ Get number of turn points """
        return len(self._turn_points)

    @property
    def vertices_3d(self) -> np.ndarray:
        """ Reference to 3d vertices """
        return self._vertex_data[:, :3]

    @property
    def vertices_2d(self) -> np.ndarray:
        """ Reference to 2d vertices (x, y only) """
        return self._vertex_data[:, :2]

    @property
    def trimesh(self) -> Trimesh:
        """ Create compute structure for collision detection """
        if self._trimesh is None:
            self._trimesh = Trimesh(vertices=self._vertex_data[:, :3],
                                    faces=self._index_data,
                                    process=True, validate=True)
        return self._trimesh

    @property
    def annotations(self) -> dict:
        """ Get dictionary of named point to location """
        return self._annotations

    def place_at_origin(self):
        """ Ensure object is stood upright (bottom at y=0) center x, z at 0, 0 """
        x_mean = self._vertex_data[:, 0].mean()
        y_min = self._vertex_data[:, 1].min()
        z_mean = self._vertex_data[:, 2].mean()
        origin_array = (x_mean, y_min, z_mean)

        self._vertex_data[:, :3] -= origin_array

        for annotation_point in self._annotations.values():
            annotation_point -= origin_array

        if self._turn_points is not None:
            self._turn_points -= origin_array

        return origin_array

    def scale_vertices(self, scalar: float):
        """ Scale vertices by a constant """
        self._vertex_data[:, :3] *= scalar

        for annotation_point in self._annotations.values():
            annotation_point *= scalar

        if self._turn_points is not None:
            self._turn_points *= scalar

    def offset_vertices(self, offset: Union[Tuple[float, float, float], np.ndarray],
                        mask: Optional[np.ndarray] = None):
        """ Update vertex locations in place by a fixed offset """
        if mask is None:
            self._vertex_data[:, :3] += offset
        else:
            self._vertex_data[mask, :3] += offset

        # Once we start running the simulation, stop updating turn-points as they are not phsyical points
        # Another way to handle this is for turn-points ect. to index a vertex
        if (isinstance(offset, np.ndarray) and len(offset.shape) == 1) \
           or isinstance(offset, tuple) or isinstance(offset, list):

            for annotation_point in self._annotations.values():
                annotation_point += offset

            if self._turn_points is not None:
                self._turn_points += offset

    def clamp_above_zero(self):
        """ Ensure y vertices are always above 0 """
        self._vertex_data[:, 1] = np.maximum(self._vertex_data[:, 1], 0.)

    def flip_x(self):
        """ Flip over x coordinates in place over mean x coordinate """
        mean_x = self._vertex_data[:, 0].mean()
        self._vertex_data[:, 0] *= -1
        self._vertex_data[:, 0] += mean_x * 2

        for annotation_point in self._annotations.values():
            annotation_point[0] *= -1
            annotation_point[0] += mean_x * 2

        if self._turn_points is not None:
            self._turn_points[:, 0] *= -1
            self._turn_points[:, 0] += mean_x * 2

    def matrix_multiply(self, matrix: np.ndarray, origin: np.ndarray):
        """ Apply a matrix to vertices """
        offset = origin - origin @ matrix

        self._vertex_data[:, :3] @= matrix
        self._vertex_data[:, :3] += offset

        for annotation_point in self._annotations.values():
            annotation_point @= matrix
            annotation_point += offset

        if self._turn_points is not None:
            self._turn_points @= matrix
            self._turn_points += offset

    def get_annotation(self, name: str) -> np.ndarray:
        """ Get 3d location by name or None """
        return self._annotations.get(name)

    def get_turn_point_by_ind(self, ind: int) -> Optional[np.ndarray]:
        """ Get 3d location of turn-point if in index range else None """
        if ind not in range(self.nr_turn_points):
            return None
        return self._turn_points[ind]
