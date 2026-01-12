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

## Project Structure

- `project_geo.py` - Main entry point and simulation loop
- `constants.py` - All configuration constants
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
