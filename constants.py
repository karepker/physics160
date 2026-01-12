##################################################################
## CONSTANTS - Internal values (not CLI-configurable)
##################################################################

from vpython import vector, color

# keystrokes recognized
PLAY_STROKE = "f"  # will play/pause animation
STEP_STROKE = "s"  # will step through animation
BREAK_STROKE = "b"  # will end animation

# physics constants
YOUNG_MODULUS = 3.92e7
A_G = 9.8

# default spring modulus values (used when USE_BALL is False)
DEFAULT_NEIGHBOR_MODULUS = [2.94e8, 3.92e8, 3.92e8]
DEFAULT_LAYER_MODULUS = [3.92e7, 3.92e7, 3.92e7]

# Callaway golf ball data (used when USE_BALL is True)
PIECE_RADII = [0.02100, 0.018798, 0.01194]
NEIGHBOR_MODULUS = [2.94e8, 3.92e7, 3.92e7]
LAYER_MODULUS = [3.92e7, 3.92e7, 3.92e7]

# particle properties (initial velocity always zero)
PARTICLE_V0 = vector(0, 0, 0)

# model creation - geodesic parameters (DO NOT CHANGE)
SHAPE = "i"  # icosahedron
FACES = 20
VERTS = 12
GEO_M = 1  # this m and n are valid for Class I geodesic spheres
GEO_N = 0
NEIGHBOR_TOLERANCE = 1.15  # should be 1 + (%tolerance/100)
CONTACT_TOLERANCE = 1.15  # should be 1 + (%tolerance/100)

# appearance
SCENE_BACKGROUND = color.white
SCENE_FOREGROUND = color.black
CLUB_COLOR = vector(0.99, 0.99, 0.99)
