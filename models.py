##################################################################
## CLASSES
##################################################################


class Spring:
    """Represents a spring connection between particles."""
    neighbor = -1
    relation = ""
    rest = 0
    constant = 0
    modulus = 0

    def __init__(self, ind, rel, r, y, young=True):
        self.neighbor = ind
        self.relation = rel
        self.rest = r
        if young:
            self.modulus = y
            self.constant = (y * (r ** 2)) / r
        else:
            self.constant = y


class Particle:
    """Wrapper for a VPython sphere with physics properties."""

    def __init__(self, visual, velocity, mass):
        self.visual = visual  # The VPython sphere
        self.velocity = velocity
        self.mass = mass
        self.springs = []
        self.update_method = ""
        self.stored_force = None
        self.momentum = mass * velocity

    @property
    def pos(self):
        return self.visual.pos

    @pos.setter
    def pos(self, value):
        self.visual.pos = value

    @property
    def radius(self):
        return self.visual.radius

    @radius.setter
    def radius(self, value):
        self.visual.radius = value

    @property
    def color(self):
        return self.visual.color

    @color.setter
    def color(self, value):
        self.visual.color = value


class Club:
    """Wrapper for a VPython box with physics properties."""

    def __init__(self, visual, velocity):
        self.visual = visual  # The VPython box
        self.velocity = velocity
        self.norm = None
        self.point = None

    @property
    def pos(self):
        return self.visual.pos

    @pos.setter
    def pos(self, value):
        self.visual.pos = value

    @property
    def axis(self):
        return self.visual.axis

    @axis.setter
    def axis(self, value):
        self.visual.axis = value

    @property
    def length(self):
        return self.visual.length

    @length.setter
    def length(self, value):
        self.visual.length = value
