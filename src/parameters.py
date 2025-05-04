""" Common place to put all parameters of simulation """

NR_STEPS = 200  # Number of time steps to simulate for a sample
AVATAR_SCALING = 0.7  # Amount to change avatar by
VERTEX_RESOLUTION = 1  # Resolution to take number of points
GRAVITY = 9.81  # Acceleration downwards due to gravity
MAX_TENSILE_VELOCITY = 0.5  # Terminal velocity from tensile forces
TIME_DELTA = 0.01  # Time increment to make update to each piece
STRESS_WEIGHTING = 600  # Weight to apply to the stress force
STRESS_THRESHOLD = 0.05  # Percentage of resting distance where stress starts applying
SHEAR_WEIGHTING = 300  # Weight to apply to the shear force
SHEAR_THRESHOLD = 0.05  # Percentage of resting distance where shear starts applying
BEND_WEIGHTING = 150  # Weight to apply to bend force
BEND_THRESHOLD = 0.05  # Sin of angle where bending is applied
CM_PER_M = 100  # Scale of coordinates in clothing to world coordinates
FRICTION_CONSTANT = 0.05  # Constant of velocity resisting acceleration
VELOCITY_DAMPING_START = 1.0  # Amount to reduce velocity by in every step at the beginning
VELOCITY_DAMPING_END = 0.25  # Amount to reduce velocity by in every step at the end
RUN_COLLISION_DETECTION = True  # This is slow, so it can be turned off
DISTANCE_FROM_BODY = 0.025  # Default distance along normal of alignment point on avatar
SEWING_SPACING = 0.01  # Spacing between two points while doing sewing
SEWING_ADJUSTMENT_STEP = 12  # Maximum distance per second to get closer to sewing adjustment
BEND_OVER_PIECE_RADIANS = 0.4  # angle in radians to rotate point when attempting to wrap
