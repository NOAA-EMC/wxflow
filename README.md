[![pynorms](https://github.com/NOAA-EMC/wxflow/actions/workflows/pynorms.yaml/badge.svg)](https://github.com/NOAA-EMC/wxflow/actions/workflows/pynorms.yaml)
[![pytests](https://github.com/NOAA-EMC/wxflow/actions/workflows/pytests.yaml/badge.svg)](https://github.com/NOAA-EMC/wxflow/actions/workflows/pytests.yaml)
![PyPI](https://img.shields.io/pypi/v/:wxflow)

# Tools for Weather Workflows

Common set of tools used in weather workflows

## Installation
```sh
$> pip install wxflow
```

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

# Disclaimer

The United States Department of Commerce (DOC) GitHub project code is provided
on an "as is" basis and the user assumes responsibility for its use. DOC has
relinquished control of the information and no longer has responsibility to
protect the integrity, confidentiality, or availability of the information. Any
claims against the Department of Commerce stemming from the use of its GitHub
project will be governed by all applicable Federal law. Any reference to
specific commercial products, processes, or services by service mark,
trademark, manufacturer, or otherwise, does not constitute or imply their
endorsement, recommendation or favoring by the Department of Commerce. The
Department of Commerce seal and logo, or the seal and logo of a DOC bureau,
shall not be used in any manner to imply endorsement of any commercial product
or activity by DOC or the United States Government.
