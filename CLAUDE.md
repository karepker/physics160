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

- `project_geo.py` - Main simulation code
- `PROJECT_SPEC.md` - Future refactoring plans (split into modules)

## Code Architecture

The simulation uses wrapper classes to separate physics state from VPython visuals:
- `Particle` - wraps VPython `sphere` with physics properties (velocity, mass, momentum, springs)
- `Club` - wraps VPython `box` with physics properties (velocity, norm, point)

Key constants can be adjusted at the top of `project_geo.py` (mass, radius, Young's modulus, club velocity, etc.).
