""" Common place to put all parameters of simulation """

NR_SEWING_POINTS = 10  # Number of points to used to pull to sewn lines together
AVATAR_SCALING = 0.5627  # Amount to change avatar by
VERTEX_RESOLUTION = 1  # Resolution to take number of points
GRAVITY = 9.81  # Acceleration downwards due to gravity
MAX_VELOCITY = 1  # Terminal velocity of a piece (may need something more sophisticated with dampening)
TIME_DELTA = 0.01  # Time increment to make update to each piece
STRESS_WEIGHTING = 0.1  # Weight to apply to the stress force
STRESS_THRESHOLD = 0.1  # Percantage of resting distance where stress starts applying
SHEAR_WEIGHTING = 0.1
SHEAR_THRESHOLD = 0.1
