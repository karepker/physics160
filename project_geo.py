##################################################################
##################################################################
## MODELING THE DEFORMATION OF A GOLF BALL
## a project for Physics 160 by Kar Epker
##################################################################
##################################################################

from vpython import *
from numpy import array, append, empty, ediff1d, average

from config import create_config
from constants import (
    PLAY_STROKE, STEP_STROKE, BREAK_STROKE,
    PARTICLE_V0, TIMESTEP,
    SHAPE, GEO_M, GEO_N,
    SCENE_BACKGROUND, SCENE_FOREGROUND,
    CLUB_COLOR,
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

def setup_scene(config):
    """Configure the VPython scene with settings from config."""
    scene.background = SCENE_BACKGROUND
    scene.foreground = SCENE_FOREGROUND
    scene.width = config.width
    scene.height = config.height
    scene.center = vector(0, 0, 0)
    scene.range = config.scene_range

##################################################################
## INITIALIZATIONS
##################################################################

def draw_sphere(points, particle_color, config):
    """Create Particle objects from points array."""
    particles = []

    for i in range(points.shape[0]):
        point = points[i]
        visual = sphere(radius=config.particle_radius,
                        pos=vector(point[0], point[1], point[2]),
                        color=particle_color)
        particle = Particle(visual, PARTICLE_V0, config.particle_mass)
        particles.append(particle)

    return particles


def get_properties(config):
    """Get radius and modulus properties based on config."""
    return {
        'piece_radii': config.get_piece_radii(),
        'neighbor_modulus': config.get_neighbor_modulus(),
        'layer_modulus': config.get_layer_modulus(),
    }


def make_model(config):
    """Create the particle-spring model."""
    freq = 2**(config.layers - 2)

    properties = get_properties(config)
    scales = properties['piece_radii']
    neighbor_modulus = properties['neighbor_modulus']
    layer_modulus = properties['layer_modulus']
    neighbor_counter = 0
    layer_counter = 0
    colors = [color.blue, color.yellow, color.orange, color.red]
    counter = 0

    points = empty(shape=(0, 3))
    particles = []
    layers = [0]

    while freq >= 1:
        if config.debug:
            print("Layer " + str(counter) + " with freq " + str(int(freq)))

        new_points = make_sphere(SHAPE, int(freq), GEO_M, GEO_N)
        new_points *= scales[counter]
        points = append(points, new_points, axis=0)

        new_particles = draw_sphere(new_points, colors[counter], config)
        particles.extend(new_particles)

        layers.append(layers[-1] + len(new_particles))

        connect_neighbors(particles, layers[counter], neighbor_modulus[neighbor_counter], config)
        neighbor_counter += 1
        if counter > 0:
            connect_layers(particles, layers, layer_modulus[layer_counter], config)
            layer_counter += 1

        if freq == 1:
            freq = 0
        else:
            freq /= 2
        counter += 1

    # last iteration for freq == -1 (single point) is a special case
    new_points = array([[0., 0., 0.]])
    new_particles = draw_sphere(new_points, colors[counter], config)
    particles.extend(new_particles)
    layers.append(layers[-1] + len(new_particles))
    connect_layers(particles, layers, layer_modulus[layer_counter], config)

    return particles


def make_curves(particles, config):
    """Create visual curves representing spring connections."""
    curves = []

    for outer in range(len(particles)):
        particle = particles[outer]
        curves.append([])

        for spring in particle.springs:
            curve_color = color.magenta
            if spring.relation == "neighbor":
                curve_color = particle.color

            curves[outer].append(curve(pos=[particle.pos, particles[spring.neighbor].pos],
                                       radius=config.curve_radius, color=curve_color))

    return curves


def reset(config):
    """Initialize or reset the simulation state."""
    particles = make_model(config)
    club_visual = box(length=config.club_depth, width=config.club_side, height=config.club_side,
                      color=CLUB_COLOR, pos=config.club_r0)
    club = Club(club_visual, config.club_v0)
    get_club_plane(club, config)
    curves = make_curves(particles, config)

    return {
        'particles': particles,
        'club': club,
        'curves': curves,
    }

##################################################################
## SIMULATION
##################################################################

def main_loop():
    """Main simulation loop."""
    # Parse CLI args and create config
    config = create_config()

    # Setup scene
    setup_scene(config)

    # Set time variables
    t = 0
    dt = TIMESTEP

    # Get variables from initialization
    scene_info = reset(config)
    particles = scene_info['particles']
    club = scene_info['club']
    curves = scene_info['curves']
    time = label(pos=particles[-1].pos + vector(-config.ball_radius, 1.7 * config.ball_radius, -1.5 * config.ball_radius),
                 text="t = " + str(t), color=color.black)

    # Set up graphs for plotting
    graphs = setup_graphs(config)

    # Data to keep track of for plotting
    centers = []
    changes = array([])
    omegas = array([])
    last_vec = vector(0, 0, 0)

    # Set loop variables
    running = not config.debug
    last_stroke = ""
    particles[11].color = color.black
    particles[11].radius = config.particle_radius * 2

    # Track key state for edge detection
    prev_keys = set()

    while True:
        rate(100)

        keys = set(keysdown())
        new_keys = keys - prev_keys
        prev_keys = keys

        if PLAY_STROKE in new_keys:
            running = not running
            last_stroke = PLAY_STROKE

        elif STEP_STROKE in new_keys:
            running = True
            last_stroke = STEP_STROKE

        elif BREAK_STROKE in new_keys:
            break

        if running:
            scene.center = particles[-1].pos
            animate(club, particles, curves, time, t, dt, config)

            plot_info = plot(particles, centers, changes, omegas, last_vec, t, dt, graphs)
            last_vec = plot_info['current_vec']
            changes = plot_info['changes']
            omegas = plot_info['omegas']
            t += dt

            if last_stroke == STEP_STROKE:
                print("step complete", end="\n\n")
                running = False

            elif last_stroke == PLAY_STROKE:
                print("running")

            last_stroke = ""

    # Post processing
    collision = changes[1] - changes[0]
    remove_first = changes[1:]
    diffs = ediff1d(remove_first)
    print("collision is " + str(collision) + " average of diffs is " + str(average(diffs)))
    print("velocity is " + str(plot_info['vcom']))
    print("omega is " + str(average(omegas)))


if __name__ == '__main__':
    main_loop()
