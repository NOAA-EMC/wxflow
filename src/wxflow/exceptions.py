# pylint: disable=unused-argument

# ----

from collections.abc import Callable

from .logger import Logger, logit

logger = Logger(level="error", colored_log=True)

__all__ = ["WorkflowException", "WorkflowKeyError", "WorkflowTypeError", "msg_except_handle"]


class WorkflowException(Exception):
    """
    Description
    -----------

    This is the base-class for all exceptions; it is a sub-class of
    Exceptions.

    Parameters
    ----------

    msg: str

        A Python string containing a message to accompany the
        exception.

    """

    @logit(logger)
    def __init__(self: Exception, msg: str):
        """
        Description
        -----------

        Creates a new WorkflowException object.

        """

        # Define the base-class attributes.
        logger.error(msg=msg)
        super().__init__(msg)


class WorkflowKeyError(KeyError):
    """
    Description
    -----------

    This is the workflow class for KeyError exceptions; it is a sub-class of
    KeyError.

    Parameters
    ----------

    msg: str

        A Python string containing a message to accompany the
        exception.

    """

    @logit(logger)
    def __init__(self: Exception, msg: str):
        """
        Description
        -----------

        Creates a new WorkflowKeyError object.

        """

        # Define the base-class attributes.
        logger.error(msg=msg)
        super().__init__(msg)


class WorkflowTypeError(TypeError):
    """
    Description
    -----------

    This is the workflow class for TypeError exceptions; it is a sub-class of
    TypeError.

    Parameters
    ----------

    msg: str

        A Python string containing a message to accompany the
        exception.

    """

    @logit(logger)
    def __init__(self: Exception, msg: str):
        """
        Description
        -----------

        Creates a new WorkflowTypeError object.

        """

        # Define the base-class attributes.
        logger.error(msg=msg)
        super().__init__(msg)

# ----


def msg_except_handle(err_cls: object) -> Callable:
    """
    Description
    -----------

    This function provides a decorator to be used to raise specified
    exceptions.

    Parameters
    ----------

    err_cls: object

        A Python object containing the WorkflowException subclass to
        be used for exception raises.

    Parameters
    ----------

    decorator: Callable

        A Python decorator.

    """

    # Define the decorator function.
    def decorator(func: Callable):

        # Execute the caller function; proceed accordingly.
        def call_function(msg: str) -> None:

            # If an exception is encountered, raise the respective
            # exception.
            raise err_cls(msg=msg)

        return call_function

    return decorator
