import numpy as np
from python_src.componentLibrary.component import component
from python_src.componentLibrary.math import Vector3


class connectionnode:
    def __init__(self, nodeName:str, vec_relative_node_position: Vector3, vec_relative_node_direction: Vector3, vec_relative_node_orientation:Vector3, parent_component: component):      
        self.nodeName = nodeName
        self.vec_relative_node_position = vec_relative_node_position
        self.vec_relative_node_direction = vec_relative_node_direction
        self.vec_relative_node_orientation = vec_relative_node_orientation
        self.parent_component = parent_component
        self.vecOrientation = Vector3.UnitX  # Assign the unit vector in the x-direction
        self.vec_absolute_node_orientation    = None
        self.vec_absolute_node_direction = None
        self.vec_absolute_node_position = None

    @property
    def absolute(self)-> Vector3:
        return self

        ## will add conditions later.
        self.vec_relative_node_orientation = self.vecOrientation
    def update_node(self):
        """Update the absolute position, direction, and orientation based on the parent component."""
        # Update absolute position
        self.vec_absolute_orientation = self.parent_component.component_rotation_matrix + self.vec_relative_node_position+ self.parent_component.vec_component_absolute_position
        self.vec_absolute_node_direction = self.parent_component.component_rotation_matrix + self.vec_relative_node_direction
        self.vec_absolute_node_orientation = self.parent_component.component_rotation_matrix + self.vec_relative_node_orientation
        

    def __eq__(self, other):
        if not isinstance(other, self):
            return False
        return self.vec_absolute_node_position == other.vec_absolute_node_position

    def _vec_equals(self, vec1: Vector3, vec2: Vector3, tolerance: float = 0.001) -> bool:
        diff = vec1 - vec2
        return diff.dot(diff) < tolerance
    
    def __hash__(self):
        return hash(self.vec_absolute_node_position)
