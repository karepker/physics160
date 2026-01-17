##################################################################
## PHYSICS / ANIMATION
##################################################################

from vpython import vector, mag, mag2, norm, dot, cos, sin, tan, atan, radians

from constants import VERTS, NEIGHBOR_TOLERANCE, CONTACT_TOLERANCE, DAMPING
from models import Spring


def connect_layers(particles, layers, modulus, config):
    """Connect particles between adjacent layers with springs."""
    threshold = mag(particles[layers[-3]].pos - particles[layers[-2]].pos) * NEIGHBOR_TOLERANCE
    if layers[-1] - layers[-2] >= VERTS:
        threshold = mag(particles[layers[-3] + VERTS].pos - particles[layers[-2]].pos) * NEIGHBOR_TOLERANCE

    if config.debug:
        print("connecting " + str(layers[-1] - layers[-2]) + " to outer layer within " + str(threshold))

    for outer in range(layers[-2], layers[-1]):
        for inner in range(layers[-3], layers[-2]):

            distance = mag(particles[outer].pos - particles[inner].pos)

            if outer == inner and config.debug:
                raise AssertionError("two points in the same layer are trying to be connected")

            elif distance < threshold:
                particles[outer].springs.append(Spring(inner, "nested", distance, modulus, True))
                particles[inner].springs.append(Spring(outer, "nested", distance, modulus, True))


def connect_neighbors(particles, start, modulus, config):
    """Connect adjacent particles within the same layer with springs."""
    threshold = mag(particles[start + 5].pos - particles[start + 4].pos) * NEIGHBOR_TOLERANCE
    if len(particles) - start > 14:
        threshold = mag(particles[start + VERTS + 1].pos - particles[start + VERTS].pos) * NEIGHBOR_TOLERANCE

    if config.debug:
        print("connecting " + str(len(particles) - start) + " neighbors within " + str(threshold))

    for outer in range(start, len(particles)):
        for inner in range(start, len(particles)):

            distance = mag(particles[outer].pos - particles[inner].pos)

            if outer == inner:
                continue

            elif distance < threshold:
                particles[outer].springs.append(Spring(inner, "neighbor", distance, modulus, True))


def get_club_plane(club, config):
    """Find normal vector and point on a club to determine the equation for its plane."""
    if club.velocity.x == 0:
        club.norm = vector(cos(config.loft), sin(config.loft), 0)
    else:
        phi = atan(club.velocity.y / club.velocity.x)
        club.norm = vector(1, 0, 0)
        club.norm.y = tan(radians(config.loft) - phi) * club.norm.x
        club.norm = norm(club.norm)

    club.point = club.pos
    club.axis = club.norm
    club.length = config.club_depth


def update_momentum(particle, Fnet, dt):
    """Apply the momentum principle to update particle state."""
    particle.momentum += Fnet * dt
    particle.velocity = particle.momentum / particle.mass
    particle.pos += particle.velocity * dt


def find_nearest_point(point, club):
    """Find nearest point on the plane of the club to particle's position."""
    d = dot(club.norm, club.pos)
    t = (d - (dot(club.norm, point))) / mag2(club.norm)

    xp = point.x + club.norm.x * t
    yp = point.y + club.norm.y * t
    zp = point.z + club.norm.z * t

    return vector(xp, yp, zp)


def update_club(particle, club):
    """Update particle position/properties based on club position."""
    particle.pos = find_nearest_point(particle.pos, club)
    particle.velocity = club.velocity
    particle.momentum = particle.mass * particle.velocity


def determine_update_method(particles, club, dt, config):
    """Determine which method to use for updating each particle."""
    for particle in particles:
        forces = []
        for spring in particle.springs:
            stretch = mag(particle.pos - particles[spring.neighbor].pos) - spring.rest
            Fspring = -spring.constant * stretch * norm(particle.pos - particles[spring.neighbor].pos)
            forces.append(Fspring)

        Fnet = vector(0, 0, 0)
        for force in forces:
            Fnet += force
        Fnet *= DAMPING

        calc_particle_pos = particle.pos + ((particle.momentum + (Fnet * dt)) / particle.mass * dt)
        calc_club_point = club.pos + club.velocity * dt

        actual = (dot(calc_particle_pos - calc_club_point, club.norm)) / mag(club.norm)
        contact_threshold = particle.radius * CONTACT_TOLERANCE

        if actual < -contact_threshold:
            particle.update_method = "club"
        else:
            particle.update_method = "momentum"
            particle.stored_force = Fnet


def animate_particles(particles, club, dt, config):
    """Animate all particles based on their update method."""
    for particle in particles:
        if config.debug and not (particle.update_method == "momentum" or particle.update_method == "club"):
            raise AssertionError("particle update = " + particle.update_method)

        if particle.update_method == "momentum":
            update_momentum(particle, particle.stored_force, dt)
        else:
            update_club(particle, club)

        particle.update_method = ""
        particle.stored_force = None


def animate_club(club, dt):
    """Animate the club by moving it according to its velocity."""
    club.pos += club.velocity * dt


def draw_curves(particles, curves):
    """Update the position of each spring connection curve."""
    for outer in range(len(particles)):
        particle = particles[outer]

        for inner in range(len(particle.springs)):
            spring = particle.springs[inner]
            current = curves[outer][inner]
            current.modify(0, pos=particle.pos)
            current.modify(1, pos=particles[spring.neighbor].pos)

    return curves


def animate_time(pos, time, t, dt, config):
    """Display the time in the upper left hand corner of the display."""
    time.text = "t = " + str(t + dt)
    time.pos = pos + vector(-config.ball_radius, 1.7 * config.ball_radius, -1.5 * config.ball_radius)


def animate(club, particles, curves, time, t, dt, config):
    """Animate all objects for one timestep."""
    animate_time(particles[-1].pos, time, t, dt, config)

    determine_update_method(particles, club, dt, config)
    animate_club(club, dt)
    animate_particles(particles, club, dt, config)
    draw_curves(particles, curves)
