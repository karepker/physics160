##################################################################
## CONSTANTS
##################################################################

from vpython import vector, color

# simulation
DEBUG = False
LABEL = False
CURVES = True  # turn off curve drawing between points
DT_BASIS = 1e-6

# keystrokes recognized
PLAY_STROKE = "f"  # will play/pause animation
STEP_STROKE = "s"  # will step through animation
BREAK_STROKE = "b"  # will end animation

# golf ball properties
TOTAL_MASS = 45.93 / 1000  # in grams/1000 = kg
PARTICLE_MASS = TOTAL_MASS / 217
YOUNG_MODULUS = 3.92e7
USE_BALL = False
RADIUS = 0.021
DEFAULT_NEIGHBOR_MODULUS = [2.94e8, 3.92e8, 3.92e8]
DEFAULT_LAYER_MODULUS = [3.92e7, 3.92e7, 3.92e7]
PIECES = 2  # cannot be more than length of layer/neighbor modulus

# Callaway golf ball data (used when USE_BALL is True)
PIECE_RADII = [0.02100, 0.018798, 0.01194]
NEIGHBOR_MODULUS = [2.94e8, 3.92e7, 3.92e7]
LAYER_MODULUS = [3.92e7, 3.92e7, 3.92e7]

# particle properties
PARTICLE_RADIUS = RADIUS / 100
CURVE_RADIUS = 3 * RADIUS / 1000
PARTICLE_V0 = vector(0, 0, 0)

# model creation
SHAPE = "i"  # icosahedron DO NOT CHANGE
FACES = 20  # DO NOT CHANGE
VERTS = 12  # DO NOT CHANGE
GEO_M = 1  # this m and n are valid for Class I geodesic spheres DO NOT CHANGE
GEO_N = 0
NEIGHBOR_TOLERANCE = 1.15  # should be 1 + (%tolerance/100)
LAYERS = PIECES + 1

# environment
A_G = 9.8
FNET_DAMP = 0.78  # from source

# club
CLUB_DEPTH = 5 * RADIUS / 1000
CLUB_SIDE = RADIUS * 2.2
CLUB_R0 = vector(-RADIUS * 1.4, -RADIUS * 0.25, 0.0)
CLUB_V0 = vector(64.82, 0.0, 0.0)
CONTACT_TOLERANCE = 1.15  # should be 1 + (%tolerance/100)
CLUB_COLOR = vector(0.99, 0.99, 0.99)
LOFT = 0  # Degrees

# appearance
SCENE_BACKGROUND = color.white
SCENE_FOREGROUND = color.black
SCENE_WIDTH = 700
SCENE_HEIGHT = 700
SCENE_RANGE = 3 / 2 * RADIUS

# graphs
SPIN = True  # whether to make the spin graph
VELOCITIES = True  # whether to make the velocity graph
