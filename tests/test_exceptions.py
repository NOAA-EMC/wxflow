import pytest

from wxflow import WorkflowException, WorkflowKeyError, WorkflowTypeError


def test_workflow_exception() -> None:
    """
    Description
    -----------

    This function provides a unit test for the WorkflowException class.

    """

    # Raise the base-class exception.
    with pytest.raises(WorkflowException):
        msg = "Testing WorkflowException raise."
        raise WorkflowException(msg=msg)

    assert True


def test_workflow_key_error() -> None:
    """
    Description
    -----------

    This function provides a unit test for the WorkflowKeyError class.

    """

    # Raise the base-class exception.
    with pytest.raises(WorkflowKeyError):
        msg = "Testing WorkflowKeyError raise."
        raise WorkflowKeyError(msg=msg)

    assert True


def test_workflow_type_error() -> None:
    """
    Description
    -----------

    This function provides a unit test for the WorkflowTypeError class.

    """

    # Raise the base-class exception.
    with pytest.raises(WorkflowTypeError):
        msg = "Testing WorkflowTypeError raise."
        raise WorkflowTypeError(msg=msg)

    assert True
