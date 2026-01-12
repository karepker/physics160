##################################################################
##################################################################
## MODELING THE DEFORMATION OF A GOLF BALL
## a project for Physics 160 by Kar Epker
##################################################################
##################################################################

from vpython import *
from numpy import array, append, empty, linspace, ediff1d, average

from constants import (
    DEBUG, LABEL, CURVES, DT_BASIS,
    PLAY_STROKE, STEP_STROKE, BREAK_STROKE,
    PARTICLE_MASS, USE_BALL, RADIUS,
    DEFAULT_NEIGHBOR_MODULUS, DEFAULT_LAYER_MODULUS,
    PIECE_RADII, NEIGHBOR_MODULUS, LAYER_MODULUS,
    PARTICLE_RADIUS, CURVE_RADIUS, PARTICLE_V0,
    SHAPE, GEO_M, GEO_N, LAYERS,
    CLUB_DEPTH, CLUB_SIDE, CLUB_R0, CLUB_V0, CLUB_COLOR,
    SCENE_BACKGROUND, SCENE_FOREGROUND, SCENE_WIDTH, SCENE_HEIGHT, SCENE_RANGE,
    SPIN, VELOCITIES,
)
from models import Particle, Club
from geodesic import make_sphere
from physics import (
    connect_layers, connect_neighbors, get_club_plane,
    animate, draw_curves,
)
from plotting import setup_graphs, plot

##################################################################
## SCENE SETUP
##################################################################

scene.background = SCENE_BACKGROUND
scene.foreground = SCENE_FOREGROUND
scene.width = SCENE_WIDTH
scene.height = SCENE_HEIGHT
scene.center = vector(0, 0, 0)
scene.range = SCENE_RANGE

##################################################################
## INITIALIZATIONS
##################################################################

def draw_sphere(points, particle_color, add_label=False):

    # initializations
    labels = []
    particles = []

    for i in range(points.shape[0]):
        point = points[i]
        visual = sphere(radius = PARTICLE_RADIUS, pos = vector(point[0], point[1], point[2]),
                        color = particle_color)
        particle = Particle(visual, PARTICLE_V0, PARTICLE_MASS)
        particles.append(particle)

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
        
        for spring in particle.springs:

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
    club_visual = box(length = CLUB_DEPTH, width = CLUB_SIDE, height = CLUB_SIDE,
                      color = CLUB_COLOR, pos = CLUB_R0)
    club = Club(club_visual, CLUB_V0)
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
## SIMULATION
##################################################################

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

    # set up graphs for plotting
    graphs = setup_graphs()

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
            plot_info = plot(particles, centers, changes, omegas, last_vec, t, dt, graphs)
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

