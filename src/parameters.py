""" Common place to put all parameters of simulation """

# Simulation parameters
NR_STEPS = 200  # Number of time steps to simulate for a sample
AVATAR_SCALING = 0.7  # Amount to change avatar by
VERTEX_RESOLUTION = 1  # Resolution to take number of points
GRAVITY = 9.81  # Acceleration downwards due to gravity
TERMINAL_VELOCITY = 20.0  # Terminal velocity from tensile forces
TIME_DELTA = 0.01  # Time increment to make update to each piece
STRESS_WEIGHTING = 600  # Weight to apply to the stress force
STRESS_THRESHOLD = 0.1  # Percentage of resting distance where stress starts applying
SHEAR_WEIGHTING = 600  # Weight to apply to the shear force
SHEAR_THRESHOLD = 0.1  # Percentage of resting distance where shear starts applying
BEND_WEIGHTING = 600  # Weight to apply to bend force
BEND_THRESHOLD = 0.1  # Sin of angle where bending is applied
CM_PER_M = 100  # Scale of coordinates in clothing to world coordinates
VELOCITY_DAMPING_START = 1.0  # Amount to reduce velocity by in every step at the beginning
VELOCITY_DAMPING_END = 0.0  # Amount to reduce velocity by in every step at the end
DISTANCE_FROM_BODY = 0.025  # Default distance along normal of alignment point on avatar
SEWING_SPACING = 0.01  # Spacing between two points while doing sewing
SEWING_ADJUSTMENT_STEP = 0.01  # Maximum distance per second to get closer to sewing adjustment
WRAP_RADIANS = 0.4  # angle in radians to rotate point when attempting to wrap

# Cuda parameters
DEFAULT_BLOCK_SIZE = 1024  # Default cuda block size
COLLISION_BLOCK_SIZE = 64  # Block size for ray tracing algorithm

# Display parameters
MIN_CAMERA_DISTANCE_RATIO = 0.1  # Near camera distance as ratio of avatar height
DEFAULT_CAMERA_DISTANCE_RATIO = 1.0  # Initial camera distance as ratio of avatar height
MAX_CAMERA_DISTANCE_RATIO = 3.0  # Far camera distance as ratio of avatar height
FIELD_OF_VIEW = 45.0  # Field of view of camera in degrees

# Default light properties
LIGHT_POSITION_RATIO = 1.2  # Default light position above avatar
LIGHT_COLOR = (1., 1., 1.)  # Default light color
LIGHT_REFLECTIVE_STRENGTH = 2.0  # Default reflective strength
LIGHT_AMBIENT_STRENGTH = 2.0  # Default ambient strength

# Default material properties
DEFAULT_AMBIENT_WEIGHTING = (0.2, 0.2, 0.2)
DEFAULT_DIFFUSE_WEIGHTING = (0.5, 0.5, 0.5)
DEFAULT_SPECULAR_WEIGHTING = (1, 1, 1)
DEFAULT_SPECULAR_EXPONENT = 0.75
DEFAULT_OPACITY = 1.
DEFAULT_SPECULAR_TINT = 0.

# Shader paths
VERTEX_SHADER_PATH = "./src/qt/shaders/camera.vert"  # Determines vertex transform shader
FRAGMENT_SHADER_PATH = "./src/qt/shaders/material.frag"  # Determines color transform shader
