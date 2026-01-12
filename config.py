##################################################################
## CONFIGURATION - CLI argument parsing and Config class
##################################################################

import argparse
from dataclasses import dataclass
from typing import List

from vpython import vector
from numpy import linspace


@dataclass
class Config:
    """Configuration object holding all simulation parameters."""

    # Primary simulation parameters (from CLI)
    club_velocity: float
    loft: float
    ball_radius: float
    ball_mass: float
    damping: float
    timestep: float
    pieces: int
    use_callaway: bool

    # Visualization options (from CLI)
    debug: bool
    labels: bool
    curves: bool
    spin_graph: bool
    velocity_graph: bool
    width: int
    height: int

    # Derived properties
    @property
    def particle_mass(self) -> float:
        """Mass per particle (ball divided into 217 particles)."""
        return self.ball_mass / 217

    @property
    def particle_radius(self) -> float:
        """Visual radius of each particle."""
        return self.ball_radius / 100

    @property
    def curve_radius(self) -> float:
        """Visual radius of spring connection curves."""
        return 3 * self.ball_radius / 1000

    @property
    def layers(self) -> int:
        """Number of layers in the ball model."""
        return self.pieces + 1

    @property
    def club_v0(self) -> vector:
        """Initial club velocity vector."""
        return vector(self.club_velocity, 0.0, 0.0)

    @property
    def club_r0(self) -> vector:
        """Initial club position."""
        return vector(-self.ball_radius * 1.4, -self.ball_radius * 0.25, 0.0)

    @property
    def club_depth(self) -> float:
        """Thickness of the club."""
        return 5 * self.ball_radius / 1000

    @property
    def club_side(self) -> float:
        """Width/height of the club face."""
        return self.ball_radius * 2.2

    @property
    def scene_range(self) -> float:
        """Camera zoom level."""
        return 3 / 2 * self.ball_radius

    def get_piece_radii(self) -> List[float]:
        """Get radii for each ball layer."""
        from constants import PIECE_RADII
        if self.use_callaway:
            return PIECE_RADII
        return list(linspace(1.0, 0.0, num=self.layers) * self.ball_radius)

    def get_neighbor_modulus(self) -> List[float]:
        """Get spring constants for intra-layer connections."""
        from constants import NEIGHBOR_MODULUS, DEFAULT_NEIGHBOR_MODULUS
        if self.use_callaway:
            return NEIGHBOR_MODULUS
        return DEFAULT_NEIGHBOR_MODULUS

    def get_layer_modulus(self) -> List[float]:
        """Get spring constants for inter-layer connections."""
        from constants import LAYER_MODULUS, DEFAULT_LAYER_MODULUS
        if self.use_callaway:
            return LAYER_MODULUS
        return DEFAULT_LAYER_MODULUS


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Golf Ball Deformation Simulation - VPython particle-spring model",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Primary simulation parameters
    sim_group = parser.add_argument_group("Simulation Parameters")
    sim_group.add_argument(
        "-v", "--club-velocity",
        type=float, default=64.82,
        help="Club impact speed in m/s"
    )
    sim_group.add_argument(
        "-l", "--loft",
        type=float, default=0,
        help="Club loft angle in degrees"
    )
    sim_group.add_argument(
        "-r", "--ball-radius",
        type=float, default=0.021,
        help="Golf ball radius in meters"
    )
    sim_group.add_argument(
        "-m", "--ball-mass",
        type=float, default=0.04593,
        help="Total ball mass in kg"
    )
    sim_group.add_argument(
        "-d", "--damping",
        type=float, default=0.78,
        help="Force damping coefficient"
    )
    sim_group.add_argument(
        "-t", "--timestep",
        type=float, default=1e-6,
        help="Physics timestep in seconds"
    )
    sim_group.add_argument(
        "-p", "--pieces",
        type=int, default=2, choices=[1, 2, 3],
        help="Number of ball layers (1-3)"
    )
    sim_group.add_argument(
        "--use-callaway",
        action="store_true", default=False,
        help="Use Callaway golf ball properties"
    )

    # Visualization options
    vis_group = parser.add_argument_group("Visualization Options")
    vis_group.add_argument(
        "--debug",
        action="store_true", default=False,
        help="Enable debug console output"
    )
    vis_group.add_argument(
        "--labels",
        action="store_true", default=False,
        help="Show particle labels in 3D view"
    )
    vis_group.add_argument(
        "--curves", "--no-curves",
        action=argparse.BooleanOptionalAction, default=True,
        help="Show/hide spring connections between particles"
    )
    vis_group.add_argument(
        "--spin-graph",
        action="store_true", default=False,
        help="Enable spin rate graph"
    )
    vis_group.add_argument(
        "--velocity-graph",
        action="store_true", default=False,
        help="Enable velocity graph"
    )
    vis_group.add_argument(
        "--width",
        type=int, default=700,
        help="Canvas width in pixels"
    )
    vis_group.add_argument(
        "--height",
        type=int, default=700,
        help="Canvas height in pixels"
    )

    return parser.parse_args()


def create_config(args: argparse.Namespace = None) -> Config:
    """Create a Config object from parsed arguments or defaults."""
    if args is None:
        args = parse_args()

    return Config(
        club_velocity=args.club_velocity,
        loft=args.loft,
        ball_radius=args.ball_radius,
        ball_mass=args.ball_mass,
        damping=args.damping,
        timestep=args.timestep,
        pieces=args.pieces,
        use_callaway=args.use_callaway,
        debug=args.debug,
        labels=args.labels,
        curves=args.curves,
        spin_graph=args.spin_graph,
        velocity_graph=args.velocity_graph,
        width=args.width,
        height=args.height,
    )
