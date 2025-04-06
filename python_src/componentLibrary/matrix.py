import numpy as np

class Matrix:
    """Base class for matrix operations."""
    def __init__(self, rows: int, cols: int):
        self.a_matrix = np.zeros((rows, cols))  # Initialize with zeros
        self.iM = rows  # Number of rows
        self.iN = cols  # Number of columns

    def __copy__(self):
        """Create a copy of the matrix."""
        new_matrix = Matrix(self.iM, self.iN)
        new_matrix.a_matrix = np.copy(self.a_matrix)
        return new_matrix

    def __mul__(self, other):
        """Matrix multiplication."""
        if isinstance(other, Matrix):
            if self.iN != other.iM:
                raise ValueError("Error: Matrix dimensions not compatible for multiplication")
            result = Matrix(self.iM, other.iN)
            result.a_matrix = np.dot(self.a_matrix, other.a_matrix)
            return result
        elif isinstance(other, np.ndarray):  # For multiplying with a vector
            return np.dot(self.a_matrix, other)
        else:
            raise TypeError("Multiplication only supports Matrix or np.ndarray")

    def __add__(self, other):
        """Matrix addition."""
        if self.iM != other.iM or self.iN != other.iN:
            raise ValueError("Error: Matrix dimensions not compatible for addition")
        result = Matrix(self.iM, self.iN)
        result.a_matrix = self.a_matrix + other.a_matrix
        return result

    def __sub__(self, other):
        """Matrix subtraction."""
        if self.iM != other.iM or self.iN != other.iN:
            raise ValueError("Error: Matrix dimensions not compatible for subtraction")
        result = Matrix(self.iM, self.iN)
        result.a_matrix = self.a_matrix - other.a_matrix
        return result

    def __neg__(self):
        
        """Negate the matrix."""
        return Matrix(self.iM, self.iN) * -1  # Using the scalar multiplication
    
    @staticmethod
    def identity(n: int):
        """Create an n x n identity matrix."""
        return np.eye(n)

    @staticmethod
    def rotation_matrix_around_vector(vecV: np.ndarray, angle_rad: float) -> 'Matrix':
        """Create a rotation matrix around a given vector by a specified angle (in radians)."""
        vec_axis = vecV / np.linalg.norm(vecV)  # Normalize the vector

        # Rodrigues rotation matrix components
        W = np.zeros((3, 3))
        W[0, 1] = -vec_axis[2]
        W[0, 2] = vec_axis[1]
        W[1, 0] = vec_axis[2]
        W[1, 1] = 0
        W[1, 2] = -vec_axis[0]
        W[2, 0] = -vec_axis[1]
        W[2, 1] = vec_axis[0]
        W[2, 2] = 0

        # Using the identity matrix
        I = Matrix.identity(3)

        # Calculate the rotation matrix using Rodrigues' formula
        rotation_matrix = I + (np.sin(angle_rad) * W) + ((1 - np.cos(angle_rad)) * (W @ W))

        return rotation_matrix

    @staticmethod
    def rotation_matrix_to_move_vector(vec1: np.ndarray, vec2: np.ndarray) -> 'Matrix':
        """Create a rotation matrix that rotates vec1 to align with vec2."""
        if np.all(vec1 == 0) or np.all(vec2 == 0):
            raise ValueError("Error: Vector cannot be zero")

        vec3 = np.cross(vec1, vec2)

        # Check for magnitude near zero
        tolerance = 1e-5
        if np.linalg.norm(vec3) < tolerance:
            vec3 = np.array([1, 0, 0])  # Unit X
            if np.linalg.norm(np.cross(vec1, vec3)) < tolerance:
                vec3 = np.array([0, 1, 0])  # Unit Y
            vec3 = vec3 - np.dot(vec1, vec3) * vec1

        vec3 = vec3 / np.linalg.norm(vec3)  # Normalize vec3
        fVec1Mag = np.linalg.norm(vec1)
        fVec2Mag = np.linalg.norm(vec2)
        fCosAngle = np.dot(vec1, vec2) / (fVec1Mag * fVec2Mag)

        # Round value to avoid floating point errors
        fCosAngle = round(fCosAngle, 5)
        fAngle = np.arccos(fCosAngle)

        rotation_matrix = Matrix.rotation_matrix_around_vector(vec3, fAngle)
        return rotation_matrix


class IdentityMatrix(Matrix):
    """Class for creating identity matrices."""
    def __init__(self, n: int):
        """Create an n x n identity matrix."""
        super().__init__(n, n)  # Initialize the base Matrix with n rows and n columns
        self.a_matrix = np.eye(n)  # Overwrite with the identity matrix

