from typing import List

import numpy as np
from connectionNode import ConnectionNode
from matrix import IdentityMatrix

class Component:
    def __init__(self, 
                 str_name: str = "Undefined Component", 
                 str_stl_file_name: str = None,
                 connection_nodes: List[ConnectionNode] = None,
                 density_field: DensityField = None):
        
        self.o_parent_node = None  # ConnectionNode
        self.o_child_node = None  # ConnectionNode
        self.f_angle_deg = 0.0

        self.list_connection_nodes: List[ConnectionNode] = connection_nodes if connection_nodes is not None else []
        self.str_name = str_name
        self.vec_component_absolute_position = np.zeros(3)  # Equivalent to Vector3.Zero
        self.o_component_rotation_matrix = IdentityMatrix(3)  # 3x3 Identity Matrix

        self.geo_geometry = None  # Geometry
        self.str_geometry_colour = "TOMATO"
        self.den_density = density_field  # DensityField

        # Load geometry if STL filename is provided
        if str_stl_file_name is not None:
            self.load_geometry_from_file(str_stl_file_name)


    
    @property
    def oComponentRotationMatrix(self) -> int:
            """ Get number of vertices """
            return  IdentityMatrix(3)  # 3x3 Identity Matrix
    
    @property
    def vecComponentAbsolutePosition(self) -> int:
            """ Get number of vertices """
            return  np.zeros(3)  # 3x3 Identity Matrix

    

    
    def load_geometry_from_file(self, file_name: str):
        """Load geometry from an STL file."""
        # Placeholder for geometry loading by stl obj etc
        # Example: self.geo_geometry = load_stl(file_name)
        pass

    def voxelize_geometry(self):
        """Voxelize the geometry of the component."""
        if self.geo_geometry is not None:
            # Placeholder for the voxelization logic
            self.den_density = self.voxelize(self.geo_geometry)

    def voxelize(self, geometry: Geometry) -> DensityField:
        """Convert geometry to a density field."""
        # Placeholder for voxelization logic
        pass