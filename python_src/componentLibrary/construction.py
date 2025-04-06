import numpy as np
from typing import List
from copy import deepcopy
from connectionNode import ConnectionNode
from matrix import IdentityMatrix, Matrix

class Construction:
    def __init__(self, root_component=None, other_construction=None):
        self.list_all_connection_nodes: List[ConnectionNode] = []
        self.list_available_connection_nodes: List[ConnectionNode] = []
        self.den_complete_density: DensityField = None
        self.geo_complete_geometry: Geometry = None
        self.o_complete_rotation_matrix = IdentityMatrix.identity(3)  # Assuming it's a numpy 3x3 matrix
        self.vec_complete_absolute_position = np.zeros(3)
        self.list_components: List[Component] = []
        self.Sh = Shapers()

        if root_component:
            for node in root_component.list_connection_nodes:
                self.list_all_connection_nodes.append(node)
                self.list_available_connection_nodes.append(node)

            self.list_components.append(root_component)

        elif other_construction:
            for node in other_construction.list_all_connection_nodes:
                self.list_all_connection_nodes.append(ConnectionNode(node))

            for node in other_construction.list_available_connection_nodes:
                self.list_available_connection_nodes.append(ConnectionNode(node))

            # Assumes DensityField has a copy constructor or similar mechanism
            self.den_complete_density = DensityField(other_construction.den_load_construction())

            self.list_components = list(other_construction.list_components)

    def den_load_construction(self):
        return self.den_complete_density

    def geo_load_construction(self):
        return self.geo_complete_geometry


    def add_to_construction(self, node_on_construction, component, node_on_component, angle_deg):
        if not self.is_node_available(node_on_construction) or not component.is_node_valid(node_on_component):
            raise Exception("Error: one or more of the specified connection points are invalid - do not connect multiple components to the same node")
        
        self.list_all_connection_nodes.extend(component.list_connection_nodes)
        self.list_available_connection_nodes.extend(component.list_connection_nodes)
        self.list_available_connection_nodes.remove(node_on_construction)
        self.list_available_connection_nodes.remove(node_on_component)

        if component.b_move_component:
            component.o_parent_node = node_on_construction
            component.o_child_node = node_on_component
            component.f_angle_deg = angle_deg

            direction_rotation_matrix = Matrix.rotation_matrix_to_move_vector(
                node_on_component.vec_absolute_node_direction,
                -node_on_construction.vec_absolute_node_direction
            )

            component.o_component_rotation_matrix = direction_rotation_matrix @ component.o_component_rotation_matrix
            component.vec_component_absolute_position = (
                node_on_construction.vec_absolute_node_position -
                component.o_component_rotation_matrix @ node_on_component.vec_relative_node_position
            )
            component.update_connection_nodes()

            tolerance = 0.01
            if np.linalg.norm(component.o_child_node.vec_absolute_node_orientation +
                            component.o_parent_node.vec_absolute_node_orientation) < tolerance:
                alignment_rotation = Matrix.rotation_matrix_around_vector(
                    component.o_parent_node.vec_absolute_node_direction,
                    np.pi
                )
            else:
                alignment_rotation = Matrix.rotation_matrix_to_move_vector(
                    component.o_child_node.vec_absolute_node_orientation,
                    component.o_parent_node.vec_absolute_node_orientation
                )

            additional_rotation = Matrix.rotation_matrix_around_vector(
                component.o_parent_node.vec_absolute_node_direction,
                np.radians(angle_deg)
            )
            component.o_component_rotation_matrix = (
                additional_rotation @ alignment_rotation @ component.o_component_rotation_matrix
            )
            component.vec_component_absolute_position = (
                node_on_construction.vec_absolute_node_position -
                component.o_component_rotation_matrix @ node_on_component.vec_relative_node_position
            )
            component.update_connection_nodes()

        self.list_components.append(component)
    def add_sub_construction(self, node_on_construction, sub_construction, node_on_subconstruction, angle_deg):
        if not self.is_node_available(node_on_construction) or not sub_construction.is_node_available(node_on_subconstruction):
            raise Exception("Error: one or more of the specified connection points are invalid - do not connect multiple components to the same node")

        sub_root = sub_construction.list_components[0]
        sub_root.o_parent_node = node_on_construction
        sub_root.o_child_node = node_on_subconstruction
        sub_root.f_angle_deg = angle_deg

        self.list_all_connection_nodes.extend(sub_construction.list_all_connection_nodes)
        self.list_available_connection_nodes.extend(sub_construction.list_available_connection_nodes)
        self.list_available_connection_nodes.remove(node_on_construction)
        self.list_available_connection_nodes.remove(node_on_subconstruction)

        rotation_matrix = Matrix.rotation_matrix_to_move_vector(
            node_on_subconstruction.vec_absolute_node_direction,
            -node_on_construction.vec_absolute_node_direction
        )

        additional_rotation = Matrix.rotation_matrix_around_vector(
            rotation_matrix @ node_on_subconstruction.vec_absolute_node_direction,
            np.radians(angle_deg)
        )
        rotation_matrix = additional_rotation @ rotation_matrix

        sub_construction.o_complete_rotation_matrix = (
            sub_construction.o_complete_rotation_matrix @ rotation_matrix
        )
        sub_construction.vec_complete_absolute_position = (
            node_on_construction.vec_absolute_node_position -
            sub_construction.o_complete_rotation_matrix @ node_on_subconstruction.vec_relative_node_position
        )

        sub_construction.update_connection_nodes()

        self.list_components.extend(sub_construction.list_components)

    def is_node_available(self, node: ConnectionNode) -> bool:
        """Check if the given node is available for connection."""
        return node in self.list_available_connection_nodes

    def is_node_valid(self, construction: 'Construction', node: ConnectionNode) -> bool:
        """Check if the given node is valid in the specified construction."""
        return node in construction.list_all_connection_nodes
