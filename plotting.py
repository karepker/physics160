##################################################################
## PLOTTING
##################################################################

from vpython import vector, graph, gdots, color, mag, norm, dot, cross, acos
from numpy import append

from constants import SPIN, VELOCITIES


def setup_graphs():
    """Create and return the graph objects for velocity/spin plotting."""
    velocity_graph = graph(
        width=600, height=300, background=color.white,
        foreground=color.black, xtitle="t (s)", ytitle="velocity (m/s)",
        title="Velocity (m/s) vs. time"
    )

    graphs = {
        'v_com': gdots(graph=velocity_graph, color=color.yellow, label="CoM velocity"),
        'spin': gdots(graph=velocity_graph, color=color.green, label="spin"),
        'v_center': gdots(graph=velocity_graph, color=color.blue, label="center velocity"),
    }

    return graphs


# get velocity of the center of mass for plotting
def get_com(particles):

    # set initial variables
    v = vector(0, 0, 0)
    r = vector(0, 0, 0)
    total_mass = 0

    # for every particle in the array
    for particle in particles:

        # perform appropriate calculations
        r += particle.mass * particle.pos
        v += particle.mass * particle.velocity
        total_mass += particle.mass

    # return the velocity of the center of mass
    return {'vcom': v / total_mass, 'rcom': r / total_mass}


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


def plot(particles, centers, changes, omegas, last_vec, t, dt, graphs):
    """
    Update plots with current simulation state.

    Args:
        particles: List of Particle objects
        centers: List tracking center velocities
        changes: Array of times when velocity slope changed sign
        omegas: Array of angular velocities
        last_vec: Previous direction vector for spin calculation
        t: Current time
        dt: Time step
        graphs: Dict with 'v_com', 'spin', 'v_center' gdots objects

    Returns:
        Dict with rcom, vcom, current_vec, changes, omegas
    """
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
        omega = dtheta / dt
        omegas = append(omegas, omega)
        last_vec = current_vec
        graphs['spin'].plot(pos=(t, omega))

    # take care of velocity plotting
    centers.append(center.velocity)
    if len(centers) > 2:
        old_slope = mag(centers[-2]) - mag(centers[-3])
        slope = mag(centers[-1]) - mag(centers[-2])
        if change_in_sign(old_slope, slope):
            changes = append(changes, t)

    if VELOCITIES:
        graphs['v_com'].plot(pos=(t, mag(vcom)))
        graphs['v_center'].plot(pos=(t, mag(center.velocity)))

    plot_info = {}
    plot_info['rcom'] = rcom
    plot_info['vcom'] = vcom
    plot_info['current_vec'] = current_vec
    plot_info['changes'] = changes
    plot_info['omegas'] = omegas
    return plot_info
