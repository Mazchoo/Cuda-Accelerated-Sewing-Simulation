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
    def __init__(self, vertex_data: np.ndarray, index_data: np.ndarray,
                 texture_data: dict, annotations: Optional[dict] = None):
        self._vertex_data = vertex_data
        self._index_data = index_data
        self._texture_data = texture_data

        self._trimesh = None
        self._annotations = annotations if annotations is not None else {}

        self.place_at_origin()

    @property
    def nr_vertices(self) -> int:
        """ Get number of vertices """
        return len(self._vertex_data)

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

        self._vertex_data[:, 0] -= x_mean
        self._vertex_data[:, 1] -= y_min
        self._vertex_data[:, 2] -= z_mean

        for annotation_point in self._annotations.values():
            annotation_point[0] -= x_mean
            annotation_point[1] -= y_min
            annotation_point[2] -= z_mean

    def scale_vertices(self, scalar: float):
        """ Scale vertices by a constant """
        self._vertex_data[:, :3] *= scalar

        for annotation_point in self._annotations.values():
            annotation_point *= scalar

    def offset_vertices(self, offset: Union[Tuple[float, float, float], np.ndarray],
                        mask: Optional[np.ndarray] = None):
        """ Update vertex locations in place by a fixed offset """
        if mask is None:
            self._vertex_data[:, :3] += offset
        else:
            self._vertex_data[mask, :3] += offset

        # Assumption: If all positions are changing, annotations only change by the average
        # This does not matter much if the annotations are not re-used
        if isinstance(offset, np.ndarray) and len(offset.shape) == 2:
            annotation_offset = offset.mean(axis=0)
        else:
            annotation_offset = offset

        for annotation_point in self._annotations.values():
            annotation_point += annotation_offset

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

    def matrix_multiply(self, matrix: np.ndarray):
        """ Apply a matrix to vertices """
        self._vertex_data[:, :3] @= matrix

    def get_annotation(self, name: str) -> np.ndarray:
        """ Get 3d location by name or None """
        return self._annotations.get(name)
