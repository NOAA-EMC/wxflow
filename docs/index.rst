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

A Python library of common tools used in weather workflows.

Installation
------------

.. code-block:: bash

    pip install wxflow

Description
-----------

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


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   API Reference <api>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
