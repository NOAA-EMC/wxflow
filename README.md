[![pynorms](https://github.com/NOAA-EMC/wxflow/actions/workflows/pynorms.yaml/badge.svg)](https://github.com/NOAA-EMC/wxflow/actions/workflows/pynorms.yaml)
[![pytests](https://github.com/NOAA-EMC/wxflow/actions/workflows/pytests.yaml/badge.svg)](https://github.com/NOAA-EMC/wxflow/actions/workflows/pytests.yaml)

# Tools for Weather Workflows

Common set of tools used in weather workflows

## Installation
Simple installation instructions
```sh
$> git clone https://github.com/noaa-emc/wxflow
$> cd wxflow
$> pip install .
```

It is not required to install this package.  Instead,
```sh
$> cd wxflow
$> export PYTHONPATH=${PWD}/src/wxflow
```
would put this package in the `PYTHONPATH`

### Note:
These instructions will be updated and the tools are under development.

### Running python tests:
Simple instructions to enable executing pytests manually
```sh
# Create a python virtual environment and step into it
$> cd wxflow
$> python3 -m venv venv
$> source venv/bin/activate

# Install `wxflow` with the developer requirements
(venv) $> pip install .[dev]
# NOTE: on a macOS, may need to specify ."[dev]" if using zsh

# Run pytests
(venv) $> pytest -v
```
