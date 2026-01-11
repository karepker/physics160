# Modeling the deformation of a golf ball

Final project for Physics 160 implemented with VPython

## Objective

Use a ball-spring model of a golf ball to simulate what happens when a golf ball is hit with a club

## Requirements

* Python 3.12+ (managed via pyenv)
* Dependencies managed via pipenv

## Setup

```bash
pyenv install 3.12.12  # if not already installed
pipenv install --python 3.12.12
```

## Running the simulation

```bash
pipenv run python project_geo.py
```

The simulation opens in your browser via VPython.

### Controls

* **f** - play/pause animation
* **s** - step through one frame
* **b** - break/exit simulation

## Configuration

Key simulation parameters can be adjusted at the top of `project_geo.py`:
* Golf ball properties (mass, radius, Young's modulus)
* Club properties (velocity, loft angle)
* Simulation settings (timestep, damping)

## Results and more detailed information

See report/Report.pdf for a detailed report of how the simulation was created and results
