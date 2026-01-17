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

**Visualization Options:**
- `--debug` - Enable debug console output
- `--width, --height` - Canvas dimensions in pixels (default: 700)

**Examples:**
```bash
# Run with slower club speed and 10-degree loft
pipenv run python project_geo.py --club-velocity 50 --loft 10

# Enable debug mode
pipenv run python project_geo.py --debug
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

Key constants can be adjusted in `constants.py` (ball mass, damping, timestep, Young's modulus, etc.).
