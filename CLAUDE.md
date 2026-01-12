# Golf Ball Deformation Simulation

A VPython simulation modeling the deformation of a golf ball upon club impact, using a geodesic sphere particle-spring model.

## Environment

This project uses **pyenv** and **pipenv** for Python version and dependency management.

- Run all Python commands with: `pipenv run python <script>`
- Syntax check: `pipenv run python -m py_compile project_geo.py`

## Running the Simulation

```bash
pipenv run python project_geo.py
```

The simulation opens in a browser via VPython. Controls:
- **f** - play/pause animation
- **s** - step through one frame
- **b** - break/exit simulation

### Command Line Options

Run `pipenv run python project_geo.py --help` to see all options.

**Simulation Parameters:**
- `-v, --club-velocity` - Club impact speed in m/s (default: 64.82)
- `-l, --loft` - Club loft angle in degrees (default: 0)
- `-r, --ball-radius` - Golf ball radius in meters (default: 0.021)
- `-m, --ball-mass` - Total ball mass in kg (default: 0.04593)
- `-d, --damping` - Force damping coefficient (default: 0.78)
- `-t, --timestep` - Physics timestep in seconds (default: 1e-6)
- `-p, --pieces` - Number of ball layers 1-3 (default: 2)
- `--use-callaway` - Use Callaway golf ball properties

**Visualization Options:**
- `--debug` - Enable debug console output
- `--labels` - Show particle labels in 3D view
- `--curves / --no-curves` - Show/hide spring connections (default: on)
- `--spin-graph` - Enable spin rate graph
- `--velocity-graph` - Enable velocity graph
- `--width, --height` - Canvas dimensions in pixels (default: 700)

**Examples:**
```bash
# Run with slower club speed and 10-degree loft
pipenv run python project_geo.py --club-velocity 50 --loft 10

# Enable debug mode with velocity graphing
pipenv run python project_geo.py --debug --velocity-graph

# Use Callaway ball properties, hide spring curves
pipenv run python project_geo.py --use-callaway --no-curves
```

## Project Structure

- `project_geo.py` - Main entry point and simulation loop
- `config.py` - CLI argument parsing and Config class
- `constants.py` - Internal constants (not CLI-configurable)
- `models.py` - Data classes (Spring, Particle, Club)
- `geodesic.py` - Geodesic sphere generation (Adrian Rossiter's code)
- `physics.py` - Physics calculations and animation functions
- `plotting.py` - Graph setup and plotting functions

## Code Architecture

The simulation uses wrapper classes (in `models.py`) to separate physics state from VPython visuals:
- `Particle` - wraps VPython `sphere` with physics properties (velocity, mass, momentum, springs)
- `Club` - wraps VPython `box` with physics properties (velocity, norm, point)
- `Spring` - represents spring connections between particles

Key constants can be adjusted in `constants.py` (mass, radius, Young's modulus, club velocity, etc.).
