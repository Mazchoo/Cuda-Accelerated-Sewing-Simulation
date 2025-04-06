import numpy as np
from component import Component

class ConnectionNode:
    def __init__(self, str_node_name: str, vec_relative_node_position: np.ndarray,
                 vec_relative_node_direction: np.ndarray, vec_relative_node_orientation: np.ndarray,
                 parent_component: Component):
        self.o_parent_component = parent_component
        self.str_node_name = str_node_name
        self.vec_relative_node_position = vec_relative_node_position
        self.vec_relative_node_direction = vec_relative_node_direction / np.linalg.norm(vec_relative_node_direction)  # Normalize
        
        # Calculate normalized orientation vector
        vec_orientation = vec_relative_node_orientation - np.dot(self.vec_relative_node_direction, vec_relative_node_orientation) * self.vec_relative_node_direction
        vec_orientation_norm = np.linalg.norm(vec_orientation)

        if vec_orientation_norm < 1e-6:  # Tolerance for comparison
            if np.array_equal(self.vec_relative_node_direction, np.array([1, 0, 0])) or np.array_equal(self.vec_relative_node_direction, np.array([-1, 0, 0])):
                self.vec_relative_node_orientation = np.array([0, 1, 0])  # Unit Y
            else:
                self.vec_relative_node_orientation = np.array([1, 0, 0])  # Unit X
        else:
            self.vec_relative_node_orientation = vec_orientation / vec_orientation_norm  # Normalize

        self.vec_absolute_node_position = np.zeros(3)  # Will be updated later
        self.vec_absolute_node_direction = np.zeros(3)  # Will be updated later
        self.vec_absolute_node_orientation = np.zeros(3)  # Will be updated later

        self.update_node()  # Initialize absolute position and direction

    def __init__(self):
        """Default constructor."""
        self.o_parent_component = None
        self.str_node_name = ""
        self.vec_relative_node_position = np.array([1, 0, 0])  # Default to Unit X
        self.vec_relative_node_direction = np.array([1, 0, 0])  # Default to Unit X
        self.vec_absolute_node_position = np.zeros(3)
        self.vec_absolute_node_direction = np.zeros(3)
        self.vec_relative_node_orientation = np.array([0, 1, 0])  # Default to Unit Y
        self.vec_absolute_node_orientation = np.zeros(3)

    def __copy__(self):
        """Create a shallow copy of the current instance."""
        new_node = ConnectionNode(
            self.str_node_name,
            self.vec_relative_node_position.copy(),
            self.vec_relative_node_direction.copy(),
            self.vec_relative_node_orientation.copy(),
            self.o_parent_component  # Retaining reference to parent component
        )
        # Copy other necessary attributes
        new_node.vec_absolute_node_position = self.vec_absolute_node_position.copy()
        new_node.vec_absolute_node_direction = self.vec_absolute_node_direction.copy()
        new_node.vec_absolute_node_orientation = self.vec_absolute_node_orientation.copy()
        return new_node

    def update_node(self):
        """Update absolute position and direction based on the parent component."""
        self.vec_absolute_node_position = (
            self.o_parent_component.oComponentRotationMatrix @ self.vec_relative_node_position +
            self.o_parent_component.vecComponentAbsolutePosition
        )
        self.vec_absolute_node_direction = self.o_parent_component.oComponentRotationMatrix @ self.vec_relative_node_direction
        self.vec_absolute_node_orientation = self.o_parent_component.oComponentRotationMatrix @ self.vec_relative_node_orientation
