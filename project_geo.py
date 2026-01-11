##################################################################
##################################################################
## MODELING THE DEFORMATION OF A GOLF BALL
## a project for Physics 160 by Kar Epker
##################################################################
##################################################################

import collections
import math
from vpython import *
from numpy import array, append, empty, linspace, ediff1d, average
#from vpython.graph import *

##################################################################
## CONSTANTS
##################################################################

# simulation
DEBUG = False
LABEL = False
CURVES = True # turn off curve drawing between points
DT_BASIS = 1e-6

# keystrokes recognized
PLAY_STROKE = "f" # will play/pause animation
STEP_STROKE = "s" # will step through animation
BREAK_STROKE = "b" # will end animation

# golf ball properties
TOTAL_MASS = 45.93/1000 # in grams/1000 = kg
PARTICLE_MASS = TOTAL_MASS/217
YOUNG_MODULUS = 3.92e7
USE_BALL = False
RADIUS = 0.021
DEFAULT_NEIGHBOR_MODULUS = [2.94e8, 3.92e8, 3.92e8]
DEFAULT_LAYER_MODULUS = [3.92e7, 3.92e7, 3.92e7]
PIECES = 2 # cannot be more than length of layer/neighbor modulus

if USE_BALL: # data for a Callaway golf ball
    PIECE_RADII = [0.02100, 0.018798, 0.01194]
    NEIGHBOR_MODULUS = [2.94e8, 3.92e7, 3.92e7]
    LAYER_MODULUS = [3.92e7, 3.92e7, 3.92e7]

# particle properties
PARTICLE_RADIUS = RADIUS/100
CURVE_RADIUS = 3 * RADIUS/1000
PARTICLE_V0 = vector(0, 0, 0)

# model creation
SHAPE = "i" # icosahedron DO NOT CHANGE
FACES = 20 # DO NOT CHANGE
VERTS = 12 # DO NOT CHANGE
GEO_M = 1 # this m and n are valid for Class I geodesic spheres DO NOT CHANGE
GEO_N = 0
NEIGHBOR_TOLERANCE = 1.15 # should be 1 + (%tolerance/100)
LAYERS = PIECES + 1

# environment
A_G = 9.8
FNET_DAMP = 0.78 # from source

# club
CLUB_DEPTH = 5 * RADIUS/1000
CLUB_SIDE = RADIUS * 2.2
CLUB_R0 = vector(-RADIUS * 1.4, -RADIUS * 0.25, 0.0)
CLUB_V0 = vector(64.82, 0.0, 0.0)
CONTACT_TOLERANCE = 1.15 # should be 1 + (%tolerance/100)
CLUB_COLOR = vector(0.99, 0.99, 0.99)
LOFT = 0 # Degrees

# appearance
scene.background = color.white
scene.foreground = color.black
scene.width = 700
scene.height = 700
scene.center = vector(0, 0, 0)
scene.range = 3/2 * RADIUS

# graphs
SPIN = True # whether to make the spin graph
VELOCITIES = True # whether to make the velocity graph

velocity_graph = graph(width=600, height=300, background=color.white,
                       foreground=color.black, xtitle="t (s)", ytitle="velocity (m/s)",
                       title="Velocity (m/s) vs. time")

v_com = gdots(graph=velocity_graph, color=color.yellow, label="CoM velocity")
spin = gdots(graph=velocity_graph, color=color.green, label="spin")
v_center = gdots(graph=velocity_graph, color=color.blue, label="center velocity")

##################################################################
## CLASSES
##################################################################

class Spring:
    neighbor = -1
    relation = ""
    rest = 0
    constant = 0
    modulus = 0
    def __init__(self, ind, rel, r, y, young = True):
        self.neighbor = ind
        self.relation = rel
        self.rest = r
        if young:
            self.modulus = y
            self.constant = (y * (r ** 2)) / r
        else:
            self.constant = y


##################################################################
## GEODESIC SPHERE CREATION, by Adrian Rossiter, adapted by Kar Epker
##################################################################
# vector functions

# convert numpy 2D array of form [n, 3] to 1D array of form [(x1, y1, z1), ... , (xn, yn, zn)]
def np_to_array(np):
    to_return = []
    for i in range(np.shape[0]):
        entry = (np[i, 0], np[i, 1], np[i, 2])
        to_return.append(entry)
    return to_return

# v0 + v1
def vec_add(v0, v1):
    return (v0[0]+v1[0], v0[1]+v1[1], v0[2]+v1[2])

# v0 - v1
def vec_subtract(v0, v1):
    return (v0[0]-v1[0], v0[1]-v1[1], v0[2]-v1[2])

# s * v0
def vec_scale(v0, s):
    return (s*v0[0], s*v0[1], s*v0[2])

# length v0
def vec_len(v0):
    return math.sqrt(v0[0]*v0[0] + v0[1]*v0[1] +v0[2]*v0[2])

# cross product v0xv1
def vec_cross(v0, v1):
    return (v1[2]*v0[1] - v1[1]*v0[2], v1[0]*v0[2] - v1[2]*v0[0], v1[1]*v0[0] - v1[0]*v0[1])

# scalar product v0.v1
def vec_scalar(v0, v1):
    return v0[0]*v1[0] + v0[1]*v1[1] + v0[2]*v1[2]


# individual shape functions

def get_octahedron(verts, faces):
    X = 0.25*math.sqrt(2)
    verts.extend( [ (0.0, 0.5, 0.0), (X, 0.0, -X), (X, 0.0, X), (-X, 0.0, X),
                   (-X, 0.0, -X), (0.0, -0.5, 0.0) ] )

    faces.extend( [ (0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 4, 1),
                   (5, 2, 1), (2, 5, 3), (3, 5, 4), (4, 5, 1) ] )


def get_tetrahedron(verts, faces):
    X = 1/math.sqrt(3)
    verts.extend( [ (-X, X, -X), (-X, -X, X), (X, X, X), (X, -X, -X) ] )
    faces.extend( [ (0, 1, 2), (0, 3, 1), (0, 2, 3), (2, 1, 3) ] )
   

def get_triangle(verts, faces):
    if 1:
        Y = math.sqrt(3.0)/12.0
        Z = -0.8
        verts.extend( [(-0.25, -Y, Z), (0.25, -Y, Z), (0.0, 2*Y, Z) ] ) 
        faces.extend( [ (0, 1, 2) ] )
    else:
        X = .525731112119133606 
        Z = .850650808352039932
        verts.extend( [(-X, 0.0, -Z), (X, 0.0, -Z), (0.0, Z, -X), (0.0, -Z, -X)]) 
        faces.extend( [(0, 1, 2), (0, 3, 1)] )


def get_icosahedron(verts, faces):
   X = .525731112119133606 
   Z = .850650808352039932

   verts.extend([(-X, 0.0, Z), (X, 0.0, Z), (-X, 0.0, -Z), (X, 0.0, -Z),
                 (0.0, Z, X), (0.0, Z, -X), (0.0, -Z, X), (0.0, -Z, -X),
                 (Z, X, 0.0), (-Z, X, 0.0), (Z, -X, 0.0), (-Z, -X, 0.0)]) 

   faces.extend([(0, 4, 1), (0, 9, 4), (9, 5, 4), (4, 5, 8), (4, 8, 1),
                 (8, 10, 1), (8, 3, 10), (5, 3, 8), (5, 2, 3), (2, 7, 3),
                 (7, 10, 3), (7, 6, 10), (7, 11, 6), (11, 0, 6), (0, 1, 6),
                 (6, 1, 10), (9, 0, 11), (9, 11, 2), (9, 2, 5), (7, 2, 11)])


# determine which polygon to create

def get_poly(poly, verts, edges, faces):
    if poly=="i":
        get_icosahedron(verts, faces)
    elif poly=="o":
        get_octahedron(verts, faces)
    elif poly=="t":
        get_tetrahedron(verts, faces)
    elif poly=="T":
        get_triangle(verts, faces)
    else:
        return 0

    for face in faces:
        for i in range(0, len(face)):
            i2 = i+1
            if(i2==len(face)):
                i2=0
         
        if face[i] < face[i2]:
            edges[(face[i], face[i2])]=0
        else:
            edges[(face[i2], face[i])]=0

    return 1

# create and arrange points

def sphere_projection(points):
    for i in range(len(points)):
        points[i]= vec_scale(points[i], 1.0/vec_len(points[i]))


def grid_to_points(grid, freq, div_by_len, f_verts, face):
    f_verts = np_to_array(f_verts)
    points = []
    v = []
    for vtx in range(3):
        v.append([(0.0, 0.0, 0.0)])
        edge_vec = vec_subtract(f_verts[(vtx+1)%3], f_verts[vtx])
        if div_by_len:
            for i in range(1, freq+1):
                v[vtx].append(vec_scale(edge_vec, float(i)/freq))
        else:
            ang = 2*math.asin(vec_len(edge_vec)/2.0)
            unit_edge_vec = vec_scale(edge_vec, 1.0/vec_len(edge_vec))
            for i in range(1, freq+1):
                length = math.sin(i*ang/freq)/math.sin(math.pi/2 + ang/2 - i*ang/freq)
                v[vtx].append(vec_scale(unit_edge_vec, length))

    for (i, j) in grid.values():
        # skip vertex
        if (i==0) + (j==0) + (i+j==freq) == 2:
            continue

        # skip edges in one direction
        if (i==0 and face[2]>face[0]) or (j==0 and face[0]>face[1]) or (i+j==freq and face[1]>face[2]):
            continue

        n = [i, j, freq - i - j]
        v_delta = vec_add(v[0][n[0]], vec_subtract(v[(0-1)%3][freq-n[(0+1)%3]], v[(0-1)%3][freq]))
        pt = vec_add(f_verts[0], v_delta)
        if not div_by_len:
            for k in [1, 2]:
                v_delta = vec_add(v[k][n[k]], vec_subtract(v[(k-1)%3][freq-n[(k+1)%3]], v[(k-1)%3][freq]))
                pt = vec_add(pt, vec_add(f_verts[k], v_delta))
            pt = vec_scale(pt, 1.0/3)
        points.append(pt)

    return points


def make_grid(freq, m, n):
    grid = collections.OrderedDict() # changed this to use Ordered dict instead of dict
    for i in range(int(2*freq/(m+n))): # changed this to cast result to an int
        for j in range(int(2*freq/(m+n))):
            x = i*(-n) + j*(m+n)
            y = i*(m+n) + j*(-m)

            if x>=0 and y>=0 and x+y <= freq:
                grid[(i,j)] = (x, y)

    return grid

def make_sphere(shape, frequency, m, n):
    verts = []
    edges = {}
    faces = []
    get_poly(SHAPE, verts, edges, faces)
    verts = array(verts)

    grid = {}
    grid = make_grid(frequency * (m**2 + m * n + n**2), 1, 0)

    points = array(verts)

    for row in faces:
        if "i" == "T":
            face_edges = (0, 0, 0) # generate points for all edges
        else:
            face_edges = row

        new_points = grid_to_points(grid, frequency, 0, array([verts[row[i]] for i in range(3)]), face_edges)
        np_new_points = array(new_points)

        if not len(new_points) == 0: # don't append if there are no new points
            points = append(points, np_new_points, axis = 0)

    sphere_projection(points)

    return points

# end geodesic sphere creation
##################################################################

##################################################################
## INITIALIZATIONS
##################################################################

# connect the layers to each other
def connect_layers(particles, layers, modulus):

    # get threshold
    threshold = mag(particles[layers[-3]].pos - particles[layers[-2]].pos) * NEIGHBOR_TOLERANCE
    if layers[-1] - layers[-2] >= VERTS:
        threshold = mag(particles[layers[-3] + VERTS].pos - particles[layers[-2]].pos) * NEIGHBOR_TOLERANCE

    if DEBUG:
        print("connecting " + str(layers[-1] - layers[-2]) + " to outer layer within " + str(threshold))
        
    for outer in range(layers[-2], layers[-1]): # inner layer
        for inner in range(layers[-3], layers[-2]): # outer layer
            
            distance = mag(particles[outer].pos - particles[inner].pos)
            
            if outer == inner and DEBUG: # INVARIANT: outer should never equal inner
                raise AssertionError("two points in the same layer are trying to be connected")
            
            elif distance < threshold: # they are neighbors
                
                particles[outer]._springs.append(Spring(inner, "nested", distance, modulus, True))
                particles[inner]._springs.append(Spring(outer, "nested", distance, modulus, True))
        

# connect the adjacent vertices within each layer to each other 
def connect_neighbors(particles, start, modulus):

    # get threshold    
    threshold = mag(particles[start + 5].pos - particles[start + 4].pos) * NEIGHBOR_TOLERANCE
    if len(particles) - start > 14:
        threshold = mag(particles[start + VERTS + 1].pos - particles[start + VERTS].pos) * NEIGHBOR_TOLERANCE

    if DEBUG:
        print("connecting " + str(len(particles) - start) + " neighbors within " + str(threshold))
    
    for outer in range(start, len(particles)): # every particle in this layer
        for inner in range(start, len(particles)): # every other particle in this layer
            
            distance = mag(particles[outer].pos - particles[inner].pos)

            if outer == inner: # they are the same
                continue
            
            elif distance < threshold: # they are neighbors
                
                # although the relation is symmetric, only add one side for speed and coding ease
                particles[outer]._springs.append(Spring(inner, "neighbor", distance, modulus, True))
         

def draw_sphere(points, particle_color, add_label = False):

    # initializations
    labels = []
    particles = []

    for i in range(points.shape[0]):
        point = points[i]
        s = sphere(radius = PARTICLE_RADIUS, pos = vector(point[0], point[1], point[2]),
                   color = particle_color)
        # Set custom physics attributes after creation
        s._velocity = PARTICLE_V0
        s._mass = PARTICLE_MASS
        s._springs = []
        s._update = ""
        s._store = None
        s._momentum = s._mass * s._velocity
        particles.append(s)

        # label the points
        if DEBUG and LABEL:
            labels.append(label(pos = particles[i].pos, text = str(int(i))))

    return particles

# get the radius for each layer
def get_properties():
    properties = {}
    piece_radii = []
    neighbor_modulus = []
    layer_modulus = []
    
    # if a ball is given
    if USE_BALL:
        properties['piece_radii'] = PIECE_RADII
        properties['neighbor_modulus'] = NEIGHBOR_MODULUS
        properties['layer_modulus'] = LAYER_MODULUS

    # default values
    else:   
        properties['piece_radii'] = linspace(1.0, 0.0, num = LAYERS) * RADIUS
        properties['neighbor_modulus'] = DEFAULT_NEIGHBOR_MODULUS
        properties['layer_modulus'] = DEFAULT_LAYER_MODULUS

    return properties


# make particle-spring model
def make_model():
    freq = 2**(LAYERS - 2)

    properties = get_properties()
    scales = properties['piece_radii']
    neighbor_modulus = properties['neighbor_modulus']
    layer_modulus = properties['layer_modulus']
    neighbor_counter = 0
    layer_counter = 0
    colors = [color.blue, color.yellow, color.orange, color.red]
    counter = 0
    
    points = empty(shape = (0, 3))
    particles = []
    layers = [0]
    
    # for each nested sphere
    while freq >= 1:
        if DEBUG:
            print("Layer " + str(counter) + " with freq " + str(int(freq)))
        
        # get and scale points
        new_points = make_sphere(SHAPE, int(freq), GEO_M, GEO_N)
        new_points *= scales[counter]
        points = append(points, new_points, axis = 0)

        # make and append set of VPython "sphere" objects for this layer
        new_particles = draw_sphere(new_points, colors[counter])
        particles.extend(new_particles)

        # keep track of indidces at which different layers start
        layers.append(layers[-1] + len(new_particles))
                          
        # connect layer to neighbors and outer layer if applicable
        connect_neighbors(particles, layers[counter], neighbor_modulus[neighbor_counter])
        neighbor_counter += 1
        if counter > 0:
            connect_layers(particles, layers, layer_modulus[layer_counter])
            layer_counter += 1
        
        # set values for the next loop
        if freq == 1:
            freq = 0
        else:
            freq /= 2
        counter += 1

    # last iteration for freq == -1 (single point) is a special case
    new_points = array([[0., 0., 0.]])
    new_particles = draw_sphere(new_points, colors[counter], LABEL)
    particles.extend(new_particles)
    layers.append(layers[-1] + len(new_particles))
    connect_layers(particles, layers, layer_modulus[layer_counter])

    return particles

# make the array of curves for the particle
def make_curves(particles):
    curves = []

    # at every spot in the array, make another array to hold curves
    for outer in range(len(particles)):
        particle = particles[outer]
        curves.append([])
        
        for spring in particle._springs:

            # determine color of curve
            curve_color = color.magenta
            if spring.relation == "neighbor":
                curve_color = particle.color
            
            curves[outer].append(curve(pos = [particle.pos, particles[spring.neighbor].pos],
                                radius = CURVE_RADIUS, color = curve_color))

    return curves

# reset
def reset():

    scene_info = {}

    # make the particle and club
    particles = make_model()
    club = box(length = CLUB_DEPTH, width = CLUB_SIDE, height = CLUB_SIDE,
               color = CLUB_COLOR, pos = CLUB_R0)
    club._velocity = CLUB_V0
    get_club_plane(club)

    if CURVES: # make curves if drawing curves
        curves = make_curves(particles)
        scene_info['curves'] = curves

    scene_info['particles'] = particles
    scene_info['club'] = club

    return scene_info

# end initialization
##################################################################

##################################################################
## ANIMATION
##################################################################

# find normal vector and point on a club to determine the equation for its plane
def get_club_plane(club):

    # special case for if atan() is infinite
    if club._velocity.x == 0:
        club._norm = vector(cos(LOFT), sin(LOFT), 0)

    # for any other case of atan()
    else:
        phi = atan(club._velocity.y/club._velocity.x)
        club._norm = vector(1, 0, 0) # assume x component is 1
        club._norm.y = tan(radians(LOFT) - phi) * club._norm.x
        club._norm = norm(club._norm)

    # set visible attributes
    club._point = club.pos
    club.axis = club._norm
    club.length = CLUB_DEPTH

# general function for the momentum principle
def update_momentum(particle, Fnet, dt):

    particle._momentum += Fnet * dt
    particle._velocity = particle._momentum/particle._mass
    old_pos = particle.pos
    particle.pos += particle._velocity * dt

# update the position/properties of the particle based on the club's position
def update_club(particle, club):
    particle.pos = find_nearest_point(particle.pos, club)
    particle._velocity = club._velocity
    particle._momentum = particle._mass * particle._velocity

# find nearest point on the plane of the club to particle's position
# solve a(x + at) + b(y + bt) + c(z + ct) = d for t
# then nearest point is: = (x + at, y + bt, z + ct)
# where ax + by + cz = d is eq of plane, (x, y, z) is point
def find_nearest_point(point, club):
    
    # compute d and t
    d = dot(club._norm, club.pos)
    t = (d - (dot(club._norm, point)))/mag2(club._norm)

    # solve for point
    xp = point.x + club._norm.x * t
    yp = point.y + club._norm.y * t
    zp = point.z + club._norm.z * t

    return vector(xp, yp, zp)

# determine which way the particle's position will be updated
# using the club or using the momentum principle
def determine_update_method(particles, club, dt):

    # loop over all particles in the array
    for particle in particles:
        
        # calculate force from each spring and put in array
        forces = []
        for spring in particle._springs:
            stretch = mag(particle.pos - particles[spring.neighbor].pos) - spring.rest
            Fspring = -spring.constant * stretch * norm(particle.pos - particles[spring.neighbor].pos)
            forces.append(Fspring)

        # vector addition of all forces in Fnet array
        Fnet = vector(0, 0, 0)
        for force in forces:
            Fnet += force
        Fnet *= FNET_DAMP

        # calculate the positions of the particle and club one dt in the future
        calc_particle_pos = particle.pos + ((particle._momentum + (Fnet * dt))/particle._mass * dt)
        calc_club_point = club.pos + club._velocity * dt

        # test for particle contact with plane and update accordingly
        actual = (dot(calc_particle_pos - calc_club_point, club._norm))/mag(club._norm)
        contact_threshold = particle.radius * CONTACT_TOLERANCE

        # if the particle is behind the plane
        if actual < -contact_threshold:
            particle._update = "club"

        # otherwise
        else:
            particle._update = "momentum"
            particle._store = Fnet
        

# animate a given particle
def animate_particles(particles, club, dt):

    # for convenience
    for particle in particles:

        # INVARIANT: particle._update must be either "momentum" or "club"
        if DEBUG and not (particle._update == "momentum" or particle._update == "club"):
            raise AssertionError("particle update = " + particle._update)
        
        # update based on momentum
        if particle._update == "momentum":
            update_momentum(particle, particle._store, dt)

        # update based on the club position
        else: # particle._update == "club"
            update_club(particle, club)

        # clean the particle's update and store variables
        particle._update = ""
        particle._store = None


# animate the club
def animate_club(club, dt):
    club.pos += club._velocity * dt

# update the position of each of the curves
def draw_curves(particles, curves):

    # for every particle in the array, draw a curve between it and all its neighbors
    for outer in range(len(particles)):
        particle = particles[outer]

        for inner in range(len(particle._springs)):
            spring = particle._springs[inner]

            # update position of corresponding curve using modern VPython API
            current = curves[outer][inner]
            current.modify(0, pos=particle.pos)
            current.modify(1, pos=particles[spring.neighbor].pos)

    return curves

# display the time in the upper left hand corner of the display
def animate_time(pos, time, t, dt):
    time.text = "t = " + str(t + dt)
    time.pos = pos + vector(-RADIUS, 1.7 * RADIUS, -1.5 * RADIUS)

# animate all objects
def animate(club, particles, curves, time, t, dt):

    animate_time(particles[-1].pos, time, t, dt)

    # animate particles and club
    determine_update_method(particles, club, dt)
    animate_club(club, dt)
    animate_particles(particles, club, dt)

    # draw the curves
    if CURVES:
        draw_curves(particles, curves)

# end animation
##################################################################

##################################################################
## SIMULATION
##################################################################

# get velocity of the center of mass for plotting
def get_com(particles):
    
    # set initial variables
    v = vector(0, 0, 0)
    r = vector(0, 0, 0)
    total_mass = 0

    # for every particle in the array
    for particle in particles:

        # perform appopriate calculations
        r += particle._mass * particle.pos
        v += particle._mass * particle._velocity
        total_mass += particle._mass

    # return the velocity of the center of mass
    return {'vcom': v/total_mass, 'rcom': r/total_mass}

# detect if first and second have a change in sign
def change_in_sign(first, second):
    if first > 0 and second > 0:
        return False
    elif first < 0 and second < 0:
        return False
    elif first == 0:
        if second == 0:
            return False
        else:
            return True
    else:
        return True

# plot
def plot(particles, centers, changes, omegas, last_vec, t, dt):

    # for convenience
    edge = particles[11]
    center = particles[-1]

    # perform calculations
    com = get_com(particles)
    rcom = com['rcom']
    vcom = com['vcom']
    current_vec = norm(rcom - edge.pos)
    
    # take care of spin plotting
    if SPIN and len(changes) > 5:
        dtheta = acos(dot(last_vec, current_vec))
        if dot(cross(last_vec, current_vec), vector(0, 0, 1)) < 0:
            dtheta = -dtheta
        omega = dtheta/dt
        omegas = append(omegas, omega)
        last_vec = current_vec
        spin.plot(pos = (t, omega))
    
    # take care of velocity plotting
    centers.append(center._velocity)
    if len(centers) > 2:
        old_slope = mag(centers[-2]) - mag(centers[-3])
        slope = mag(centers[-1]) - mag(centers[-2])
        if change_in_sign(old_slope, slope):
            changes = append(changes, t)
    
    if VELOCITIES:
        v_com.plot(pos = (t, mag(vcom)))
        v_center.plot(pos = (t, mag(center._velocity)))

    plot_info = {}
    plot_info['rcom'] = rcom
    plot_info['vcom'] = vcom
    plot_info['current_vec'] = current_vec
    plot_info['changes'] = changes
    plot_info['omegas'] = omegas
    return plot_info

# driver
def main_loop():

    # set time variables
    t = 0
    dt_basis = DT_BASIS
    dt = dt_basis

    # get variables from initialization
    scene_info = reset()
    particles = scene_info['particles']
    club = scene_info['club']
    curves = []
    time = label(pos = particles[-1].pos + vector(-RADIUS, 1.7 * RADIUS, -1.5 * RADIUS),text = "t = " + str(t),
                 color = color.black)
    if CURVES:
        curves = scene_info['curves']

    # data to keep track of for plotting
    centers = []
    changes = array([])
    omegas = array([])
    last_vec = vector(0, 0, 0)

    # set loop variables
    running = not DEBUG
    last_stroke = ""
    particles[11].color = color.black
    particles[11].radius = PARTICLE_RADIUS  * 2
    
    # Track key state for edge detection
    prev_keys = set()

    while True:
        rate(100)  # Control animation speed and allow browser updates

        keys = set(keysdown()) # keypress detection
        new_keys = keys - prev_keys  # keys just pressed this frame
        prev_keys = keys

        if PLAY_STROKE in new_keys: # play/pause (toggle)
            running = not running
            last_stroke = PLAY_STROKE

        elif STEP_STROKE in new_keys: # step
            running = True
            last_stroke = STEP_STROKE

        elif BREAK_STROKE in new_keys: # break
            break

        if running: # animate

            # update scene properties
            scene.center = particles[-1].pos
            animate(club, particles, curves, time, t, dt)

            # update quantities that have been modified in plot
            plot_info = plot(particles, centers, changes, omegas, last_vec, t, dt)
            last_vec = plot_info['current_vec']
            changes = plot_info['changes']
            omegas = plot_info['omegas']
            t += dt

            # handle keystrokes and messages
            if last_stroke == STEP_STROKE:
                print("step complete", end = "\n\n")
                running = False

            elif last_stroke == PLAY_STROKE:
                print("running")

            last_stroke = ""

    # post processing
    if VELOCITIES:
        collision = changes[1] - changes[0]
        remove_first = changes[1:]        
        diffs = ediff1d(remove_first)
        print("collision is " + str(collision) + " average of diffs is " + str(average(diffs)))
        print("velocity is " + str(plot_info['vcom']))

    if SPIN:
        print("omega is " + str(average(omegas)))

# end simulation
##################################################################

# run it like a boss
main_loop()

