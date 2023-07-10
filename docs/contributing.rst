Contributing
============

We love contributions here in ``wxflow``! If you're looking for something to work on then check out our
`issue tracker <https://github.com/noaa-emc/wxflow/issues>`_ for open issues.

If you want to make a contribution to ``wxflow`` then please raise a
`Pull Request <https://github.com/noaa-emc/wxflow/pulls>`_ on GitHub.

To help speed up the review process please ensure the following:

- The PR addresses an open issue.
- All tests are passing locally with ``pytest``.
- The project passes linting with ``isort`` and ``pycodestyle``.
- If adding a new feature you also add documentation.

Developing
----------

To check out a local copy of the project you can `fork the project on GitHub <https://github.com/noaa-emc/wxflow/fork>`_
and then clone it locally.

.. code-block:: bash

   $ git clone https://github.com/yourusername/wxflow
   $ cd wxflow

This project uses ``isort`` to sort Python import definitions alphabetically and ``pycodestyle`` as the Python style checker against conventions in PEP8.  We also support ``pre-commit`` to ensure
these have been run. To configure your local environment please install these development dependencies and set up
the commit hooks.

.. code-block:: bash

   $ pip install isort pycodestyle pre-commit
   $ pre-commit install

You can check that things are working correctly by calling pre-commit directly.

.. code-block:: bash

   $ pre-commit run --all-files
   isort......................................Passed
   pycodestyle................................Passed

These checks will be run automatically when you make a commit (if ``pre-commit`` has been installed).

Testing
-------

This project uses ``pytest`` to run tests and also to test docstring examples.

Install the test dependencies.

.. code-block:: bash

   $ pip install .dev

Run the tests.

.. code-block:: bash

   $ pytest
   === 3 passed in 0.13 seconds ===

If you are working on a new feature please add tests to ensure the feature works as expected. If you are working on
a bug fix then please add a test to ensure there is no regression.

Tests are stored in ``wxflow/tests`` and follow the pytest format.

.. code-block:: python

    from datetime import datetime
    from wxflow import to_datetime

    def test_to_datetime():
        assert to_datetime('20220314') == datetime(2022, 3, 14)

Making a Pull Request
---------------------

Once you've made your changes and are ready to make a Pull Request please ensure tests and linting pass locally before pushing to GitHub.
When making your Pull Request please include a short description of the changes, but more importantly why they are important. Perhaps by
writing a before and after paragraph with user examples.

Also consider how your title look when it appears in a changelog. Does it full describe the change to an outside user? For example
``Add support for checking supported datetime`` is a much better title than ``Fixes #56``.

.. code-block:: markdown

    # Add support for validating a string can be transformed into a datetime object

    Closes #56

    **Changes**

    This PR allows the inspection of strings to check if it can be transformed into a datetime object.

    **Before**

    If a user passed a random string to `is_supported_datetime` it would return `False`.

    ```python
    >>> from wxflow import is_supported_datetime
    >>> is_supported_datetime('2012 Jun 15, 12:23')
    False
    ```

    **After**

    If a user passes a valid, supported datetime string, it will return true


    ```python
    >>> from wxflow import is_supported_datetime
    >>> is_supported_datetime('20120615T1223z')
    True
    ```
