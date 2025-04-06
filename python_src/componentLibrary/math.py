import math

class Vector3:
    # Class-level constants for unit vectors
    UnitX = None
    UnitY = None
    UnitZ = None
    Zero = None
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f"Vector3({self.x}, {self.y}, {self.z})"

    def __add__(self, other):
        """Add two vectors."""
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        """Subtract two vectors."""
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def dot(self, other):
        """Calculate the dot product of two vectors."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """Calculate the cross product of two vectors."""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def magnitude(self):
        """Calculate the magnitude (length) of the vector."""
        return math.sqrt(self.dot(self))

    def normalize(self):
        """Return a normalized (unit) vector."""
        mag = self.magnitude()
        if mag == 0:
            return Vector3(0, 0, 0)  # Prevent division by zero
        return Vector3(self.x / mag, self.y / mag, self.z / mag)

    def scale(self, scalar: float):
        """Scale the vector by a scalar."""
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    @classmethod
    def initialize_unit_vectors(cls):
        """Initialize class-level unit vector constants."""
        cls.UnitX = Vector3(1.0, 0.0, 0.0)
        cls.UnitY = Vector3(0.0, 1.0, 0.0)
        cls.UnitZ = Vector3(0.0, 0.0, 1.0)       
        cls.Zero = Vector3(0.0, 0.0, 0.0)


# Initialize unit vectors
Vector3.initialize_unit_vectors()
