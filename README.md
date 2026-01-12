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

Simulation parameters can be configured via command-line flags. Run `--help` to see all options:

```bash
pipenv run python project_geo.py --help
```

### Simulation Parameters

| Flag | Description | Default |
|------|-------------|---------|
| `-v, --club-velocity` | Club impact speed (m/s) | 64.82 |
| `-l, --loft` | Club loft angle (degrees) | 0 |
| `-r, --ball-radius` | Golf ball radius (m) | 0.021 |
| `-m, --ball-mass` | Total ball mass (kg) | 0.04593 |
| `-d, --damping` | Force damping coefficient | 0.78 |
| `-t, --timestep` | Physics timestep (s) | 1e-6 |
| `-p, --pieces` | Number of ball layers (1-3) | 2 |
| `--use-callaway` | Use Callaway ball properties | off |

### Visualization Options

| Flag | Description | Default |
|------|-------------|---------|
| `--debug` | Enable debug console output | off |
| `--labels` | Show particle labels | off |
| `--curves / --no-curves` | Show spring connections | on |
| `--spin-graph` | Enable spin rate graph | off |
| `--velocity-graph` | Enable velocity graph | off |
| `--width` | Canvas width (pixels) | 700 |
| `--height` | Canvas height (pixels) | 700 |

### Examples

```bash
# Run with slower club speed and 10-degree loft
pipenv run python project_geo.py --club-velocity 50 --loft 10

# Enable debug mode with velocity graphing
pipenv run python project_geo.py --debug --velocity-graph

# Use Callaway ball properties, hide spring curves
pipenv run python project_geo.py --use-callaway --no-curves
```

Internal constants (geodesic parameters, tolerances) remain in `constants.py`

## Results and more detailed information

See report/Report.pdf for a detailed report of how the simulation was created and results
