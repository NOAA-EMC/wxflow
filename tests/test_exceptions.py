import pytest

from wxflow import WorkflowException, WorkflowKeyError, WorkflowTypeError

# ----


class TestWorkflowException(WorkflowException):
    """
    Description
    -----------

    This is the base-class for generic exceptions encountered within the
    wxflow/errors unit-tests module; it is a sub-class of WorkflowException.

    """

class TestWorkflowKeyError(WorkflowKeyError):
    """
    Description
    -----------

    This is the base-class for KeyError exceptions encountered within the
    wxflow/errors unit-tests module; it is a sub-class of WorkflowKeyError.

    """

class TestWorkflowTypeError(WorkflowTypeError):
    """
    Description
    -----------

    This is the base-class for TypeError exceptions encountered within the
    wxflow/errors unit-tests module; it is a sub-class of WorkflowTypeError.

    """

# ----

def test_workflow_exception() -> None:
    """
    Description
    -----------

    This function provides a unit test for the WorkflowException class.

    """

    # Raise the base-class exception.
    with pytest.raises(Exception):
        msg = "Testing WorkflowException raise."
        raise TestWorkflowException(msg=msg)

    assert True

def test_workflow_key_error() -> None:
    """
    Description
    -----------

    TThis function provides a unit test for the WorkflowKeyError class.

    """

    # Raise the base-class exception.
    with pytest.raises(Exception):
        msg = "Testing WorkflowKeyError raise."
        raise TestWorkflowKeyError(msg=msg)

    assert True

def test_workflow_type_error() -> None:
    """
    Description
    -----------

    TThis function provides a unit test for the WorkflowTypeError class.

    """

    # Raise the base-class exception.
    with pytest.raises(Exception):
        msg = "Testing WorkflowTypeError raise."
        raise TestWorkflowTypeError(msg=msg)

    assert True
