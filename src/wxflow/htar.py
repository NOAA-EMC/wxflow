from logging import getLogger
from .executable import Executable, which

__all__ = ['Htar']

logger = getLogger(__name__.split('.')[-1])


"""Class providing a set of functions to interact with the htar utility.

"""

def htar(*args) -> None:
    """Direct command builder function for htar based on the input arguments.

    `args` should consist of a set of string arguments to send to htar
    For example, Htar.htar("-cvf","/path/to/hpss/archive.tar", "<string list of files>") will execute
    htar -cvf /path/to/hpss/archive.tar <string list of files>

    """

    cmd = which("htar", required = True)

    for arg in args:
        cmd.add_default_arg(arg)

    cmd()


def create(tarball: str, fileset: list, flags: str = "") -> None:
    """ Function to write an archive to HPSS

    Parameters
    ----------
    flags : str
            String of flags to send to htar.

    tarball : str
            Full path location on HPSS to create the archive.

    fileset : list
            List containing filenames, patterns, or directories to archive
    """
    args = ("-c",)

    # Parse any htar flags
    if len(flags) > 0:
        args += tuple(flags.split(" "))

    args += ("-f", tarball,) + tuple(fileset)

    htar(*args)


def cvf(tarball: str, fileset: list) -> None:
    """ Function to write an archive to HPSS verbosely (without flags).

    Parameters
    ----------
    tarball : str
            Full path location on HPSS to create the archive.

    fileset : list
            List containing filenames, patterns, or directories to archive
    """
    create(tarball, fileset, flags = "-v")


def extract(tarball: str, fileset: list = [], flags: str = "") -> None:
    """ Function to extract an archive from HPSS via htar

    Parameters
    ----------
    flags : str
            String of flags to send to htar.

    tarball : str
            Full path location of an archive on HPSS to extract from.

    fileset : list
            List containing filenames, patterns, or directories to extract from
            the archive.  If empty, then all files will be extracted.
    """
    args = ("-x",)

    # Parse any htar flags
    if len(flags) > 0:
        args += tuple(flags.split(" "))

    args += ("-f", tarball,)

    if len(fileset) > 0:
        args += tuple(fileset)

    htar(*args)


def xvf(tarball: str = "", fileset: list = []) -> None:
    """ Function to extract an archive from HPSS verbosely (without flags).

    Parameters
    ----------
    tarball : str
            Full path location of an archive on HPSS to extract from.

    fileset : list
            List containing filenames, patterns, or directories to extract from
            the archive.  If empty, then all files will be extracted.
    """
    extract(tarball, fileset, flags = "-v")


def tell(tarball: str, flags: str = "", fileset: list = []) -> None:
    """ Function to list the contents of an archive on HPSS

    Parameters
    ----------
    flags : str
            String of flags to send to htar.

    tarball : str
            Full path location on HPSS to list the contents of.

    fileset : list
            List containing filenames, patterns, or directories to list.
            If empty, then all files will be listed.
    """
    args = ("-t",)

    # Parse any htar flags
    if len(flags) > 0:
        args += tuple(flags.split(" "))

    args += ("-f", tarball,)

    if len(fileset) > 0:
        args += tuple(fileset)

    htar(*args)
