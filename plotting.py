##################################################################
## PLOTTING
##################################################################

from vpython import vector, graph, gdots, color, mag, norm, dot, cross, acos
from numpy import append


def setup_graphs(config):
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


def get_com(particles):
    """Get velocity and position of the center of mass."""
    v = vector(0, 0, 0)
    r = vector(0, 0, 0)
    total_mass = 0

    for particle in particles:
        r += particle.mass * particle.pos
        v += particle.mass * particle.velocity
        total_mass += particle.mass

    return {'vcom': v / total_mass, 'rcom': r / total_mass}


def change_in_sign(first, second):
    """Detect if first and second have a change in sign."""
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


def plot(particles, centers, changes, omegas, last_vec, t, dt, graphs, config):
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
        config: Config object with simulation parameters

    Returns:
        Dict with rcom, vcom, current_vec, changes, omegas
    """
    edge = particles[11]
    center = particles[-1]

    com = get_com(particles)
    rcom = com['rcom']
    vcom = com['vcom']
    current_vec = norm(rcom - edge.pos)

    # Spin plotting
    if config.spin_graph and len(changes) > 5:
        dtheta = acos(dot(last_vec, current_vec))
        if dot(cross(last_vec, current_vec), vector(0, 0, 1)) < 0:
            dtheta = -dtheta
        omega = dtheta / dt
        omegas = append(omegas, omega)
        last_vec = current_vec
        graphs['spin'].plot(pos=(t, omega))

    # Velocity plotting
    centers.append(center.velocity)
    if len(centers) > 2:
        old_slope = mag(centers[-2]) - mag(centers[-3])
        slope = mag(centers[-1]) - mag(centers[-2])
        if change_in_sign(old_slope, slope):
            changes = append(changes, t)

    if config.velocity_graph:
        graphs['v_com'].plot(pos=(t, mag(vcom)))
        graphs['v_center'].plot(pos=(t, mag(center.velocity)))

    return {
        'rcom': rcom,
        'vcom': vcom,
        'current_vec': current_vec,
        'changes': changes,
        'omegas': omegas,
    }
