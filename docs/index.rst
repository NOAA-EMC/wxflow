.. wxflow documentation master file

wxflow
======

.. image:: https://img.shields.io/pypi/wxflow
    :target: https://pypi.org/project/wxflow/
    :alt: PyPI
.. image:: https://github.com/NOAA-EMC/wxflow/workflows/pynorms/badge.svg
    :target: https://github.com/NOAA-EMC/wxflow/actions/workflows/pynorms.yaml
    :alt: pynorms
.. image:: https://github.com/NOAA-EMC/wxflow/workflows/pytests/badge.svg
    :target: https://github.com/NOAA-EMC/wxflow/actions/workflows/pytests.yaml
    :alt: pytests
.. image:: https://readthedocs.org/projects/wxflow/badge/?version=latest
    :target: https://wxflow.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://codecov.io/gh/noaa-emc/wxflow/branch/develop/graph/badge.svg?token=JWTPE8Z7MH
    :target: https://codecov.io/gh/noaa-emc/wxflow
    :alt: Codecov

********
Overview
********

wxflow is a Python library of common tools used in weather workflows. It is
designed to be used in NWP applications such as GFS, GEFS, and RRFS workflows.  Some of the tools
included in wxflow are:

- **logger**: A generic program-wide logging tool.
- **yamltools**: A YAML parser that allows loading of nested yaml files and resolves environment variables.
- **timetools**: A collection of datetime tools that allows for easy transformation between the various formats of datetime used in the applications.
- **executable**: A tool that allows for running command line programs within the python environment.
  executables.
- **jinja**: A jinja tool that allows for the use of Jinja2 templates with filters.
- **task**: A task tool that allows for the use of a YAML file to configure
  tasks.

Installation
------------

.. code-block:: bash

    pip install wxflow


Disclaimer
----------

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

.. toctree::
    :hidden:
    :maxdepth: 2

    Contributing <contributing>
    Maintaining <maintaining>

.. toctree::
    :caption: Development
    :hidden:
    :maxdepth: 2

    API Reference <api>
    Function index <genindex>
