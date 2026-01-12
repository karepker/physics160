##################################################################
## PHYSICS / ANIMATION
##################################################################

from vpython import vector, mag, mag2, norm, dot, cos, sin, tan, atan, radians

from constants import (
    DEBUG, CURVES, VERTS, NEIGHBOR_TOLERANCE,
    FNET_DAMP, CONTACT_TOLERANCE, CLUB_DEPTH, LOFT, RADIUS,
)
from models import Spring


# connect the layers to each other
def connect_layers(particles, layers, modulus):

    # get threshold
    threshold = mag(particles[layers[-3]].pos - particles[layers[-2]].pos) * NEIGHBOR_TOLERANCE
    if layers[-1] - layers[-2] >= VERTS:
        threshold = mag(particles[layers[-3] + VERTS].pos - particles[layers[-2]].pos) * NEIGHBOR_TOLERANCE

    if DEBUG:
        print("connecting " + str(layers[-1] - layers[-2]) + " to outer layer within " + str(threshold))

    for outer in range(layers[-2], layers[-1]):  # inner layer
        for inner in range(layers[-3], layers[-2]):  # outer layer

            distance = mag(particles[outer].pos - particles[inner].pos)

            if outer == inner and DEBUG:  # INVARIANT: outer should never equal inner
                raise AssertionError("two points in the same layer are trying to be connected")

            elif distance < threshold:  # they are neighbors

                particles[outer].springs.append(Spring(inner, "nested", distance, modulus, True))
                particles[inner].springs.append(Spring(outer, "nested", distance, modulus, True))


# connect the adjacent vertices within each layer to each other
def connect_neighbors(particles, start, modulus):

    # get threshold
    threshold = mag(particles[start + 5].pos - particles[start + 4].pos) * NEIGHBOR_TOLERANCE
    if len(particles) - start > 14:
        threshold = mag(particles[start + VERTS + 1].pos - particles[start + VERTS].pos) * NEIGHBOR_TOLERANCE

    if DEBUG:
        print("connecting " + str(len(particles) - start) + " neighbors within " + str(threshold))

    for outer in range(start, len(particles)):  # every particle in this layer
        for inner in range(start, len(particles)):  # every other particle in this layer

            distance = mag(particles[outer].pos - particles[inner].pos)

            if outer == inner:  # they are the same
                continue

            elif distance < threshold:  # they are neighbors

                # although the relation is symmetric, only add one side for speed and coding ease
                particles[outer].springs.append(Spring(inner, "neighbor", distance, modulus, True))


# find normal vector and point on a club to determine the equation for its plane
def get_club_plane(club):

    # special case for if atan() is infinite
    if club.velocity.x == 0:
        club.norm = vector(cos(LOFT), sin(LOFT), 0)

    # for any other case of atan()
    else:
        phi = atan(club.velocity.y / club.velocity.x)
        club.norm = vector(1, 0, 0)  # assume x component is 1
        club.norm.y = tan(radians(LOFT) - phi) * club.norm.x
        club.norm = norm(club.norm)

    # set visible attributes
    club.point = club.pos
    club.axis = club.norm
    club.length = CLUB_DEPTH


# general function for the momentum principle
def update_momentum(particle, Fnet, dt):

    particle.momentum += Fnet * dt
    particle.velocity = particle.momentum / particle.mass
    old_pos = particle.pos
    particle.pos += particle.velocity * dt


# find nearest point on the plane of the club to particle's position
# solve a(x + at) + b(y + bt) + c(z + ct) = d for t
# then nearest point is: = (x + at, y + bt, z + ct)
# where ax + by + cz = d is eq of plane, (x, y, z) is point
def find_nearest_point(point, club):

    # compute d and t
    d = dot(club.norm, club.pos)
    t = (d - (dot(club.norm, point))) / mag2(club.norm)

    # solve for point
    xp = point.x + club.norm.x * t
    yp = point.y + club.norm.y * t
    zp = point.z + club.norm.z * t

    return vector(xp, yp, zp)


# update the position/properties of the particle based on the club's position
def update_club(particle, club):
    particle.pos = find_nearest_point(particle.pos, club)
    particle.velocity = club.velocity
    particle.momentum = particle.mass * particle.velocity


# determine which way the particle's position will be updated
# using the club or using the momentum principle
def determine_update_method(particles, club, dt):

    # loop over all particles in the array
    for particle in particles:

        # calculate force from each spring and put in array
        forces = []
        for spring in particle.springs:
            stretch = mag(particle.pos - particles[spring.neighbor].pos) - spring.rest
            Fspring = -spring.constant * stretch * norm(particle.pos - particles[spring.neighbor].pos)
            forces.append(Fspring)

        # vector addition of all forces in Fnet array
        Fnet = vector(0, 0, 0)
        for force in forces:
            Fnet += force
        Fnet *= FNET_DAMP

        # calculate the positions of the particle and club one dt in the future
        calc_particle_pos = particle.pos + ((particle.momentum + (Fnet * dt)) / particle.mass * dt)
        calc_club_point = club.pos + club.velocity * dt

        # test for particle contact with plane and update accordingly
        actual = (dot(calc_particle_pos - calc_club_point, club.norm)) / mag(club.norm)
        contact_threshold = particle.radius * CONTACT_TOLERANCE

        # if the particle is behind the plane
        if actual < -contact_threshold:
            particle.update_method = "club"

        # otherwise
        else:
            particle.update_method = "momentum"
            particle.stored_force = Fnet


# animate a given particle
def animate_particles(particles, club, dt):

    # for convenience
    for particle in particles:

        # INVARIANT: particle.update_method must be either "momentum" or "club"
        if DEBUG and not (particle.update_method == "momentum" or particle.update_method == "club"):
            raise AssertionError("particle update = " + particle.update_method)

        # update based on momentum
        if particle.update_method == "momentum":
            update_momentum(particle, particle.stored_force, dt)

        # update based on the club position
        else:  # particle.update_method == "club"
            update_club(particle, club)

        # clean the particle's update and store variables
        particle.update_method = ""
        particle.stored_force = None


# animate the club
def animate_club(club, dt):
    club.pos += club.velocity * dt


# update the position of each of the curves
def draw_curves(particles, curves):

    # for every particle in the array, draw a curve between it and all its neighbors
    for outer in range(len(particles)):
        particle = particles[outer]

        for inner in range(len(particle.springs)):
            spring = particle.springs[inner]

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
