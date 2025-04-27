""" Common place to put all parameters of simulation """

NR_STEPS = 200  # Number of time steps to simulate for a sample
AVATAR_SCALING = 0.5627  # Amount to change avatar by
VERTEX_RESOLUTION = 1  # Resolution to take number of points
GRAVITY = 9.81  # Acceleration downwards due to gravity
MAX_TENSILE_VELOCITY = 0.5  # Terminal velocity from tensile forces
MAX_GRAVITY_VELOCITY = 0.5  # Terminal velocity from falling
TIME_DELTA = 0.01  # Time increment to make update to each piece
STRESS_WEIGHTING = 150  # Weight to apply to the stress force
STRESS_THRESHOLD = 0.001  # Percentage of resting distance where stress starts applying
SHEAR_WEIGHTING = 100  # Weight to apply to the shear force
SHEAR_THRESHOLD = 0.001  # Percentage of resting distance where shear starts applying
BEND_WEIGHTING = 100  # Weight to apply to bend force
BEND_THRESHOLD = 0.001  # Sin of angle where bending is applied
CM_PER_M = 100  # Scale of coordinates in clothing to world coordinates
FRICTION_CONSTANT = 0.05  # Constant of velocity resisting acceleration
VELOCITY_DAMPING_START = 1.0  # Amount to reduce velocity by in every step at the beginning
VELOCITY_DAMPING_END = 0.5  # Amount to reduce velocity by in every step at the end
RUN_COLLISION_DETECTION = True  # This is slow, so it can be turned off
DISTANCE_FROM_BODY = 0.1  # Default distance along normal of alignment point on avatar
SEWING_SPACING = 0.01  # Spacing between two points while doing sewing
SEWING_WEIGHTING = 200  # Weighting to apply to sewing distance
