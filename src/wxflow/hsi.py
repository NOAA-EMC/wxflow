from logging import getLogger
from .executable import Executable, which

__all__ = ['hsi', 'get', 'put', 'ls', 'chmod', 'chgrp', 'rm', 'mkdir', 'file_exists']

logger = getLogger(__name__.split('.')[-1])


def hsi(*args) -> str:
    """Direct command builder function for hsi based on the input arguments.

    `args` should consist of a set of string arguments to send to hsi
    For example, hsi("get","some_local_file : /some/hpss/file") will execute
    hsi get some_local_file : /some/hpss/file

    Return: str
        Concatenated output and error of the hsi command.
    """

    cmd = which("hsi", required = True)

    for arg in args:
        cmd.add_default_arg(arg)

    output = cmd(output = str.split, error = str.split)

    return output


def get(source: str, target: str = "", hsi_flags: str = "") -> str:
    """ Function to get a file from HPSS via hsi

    Parameters
    ----------
    source : str
            Full path location on HPSS of the file

    target : str
            Location on the local machine to place the file.  If not specified,
            then the file will be placed in the current directory.

    hsi_flags : str
            String of flags to send to hsi.
    """
    args = []

    # Parse any hsi flags
    if len(hsi_flags) > 0:
        args.extend(hsi_flags.split(" "))

    args.append("get")
    if len(target) == 0:
        args.append(source)
    else:
        args.append(target + " : " + source)

    output = hsi(*args)

    return output


def put(source: str, target: str, hsi_flags: str = "", listing_file : str = None) -> str:
    """ Function to put a file onto HPSS via hsi

    Parameters
    ----------
    source : str
            Location on the local machine of the source file to send to HPSS.

    target : str
            Full path of the target location of the file on HPSS.

    hsi_flags : str
            String of flags to send to hsi.
    """
    args = []

    # Parse any hsi flags
    if len(hsi_flags) > 0:
        args.extend(hsi_flags.split(" "))

    args.append("put")
    args.append(source + " : " + target)
    output = hsi(*args)

    return output


def chmod(mod: str, target: str, hsi_flags: str = "", chmod_flags: str = "") -> str:
    """ Function to change the permissions of a file or directory on HPSS

    Parameters
    ----------
    mod : str
            Permissions to set for the file or directory, e.g. "640", "o+r", etc.

    target : str
            Full path of the target location of the file on HPSS.

    hsi_flags : str
            String of flags to send to hsi.

    chmod_flags : str
            Flags to send to chmod. See "hsi chmod -?" for more details.
    """

    args = []

    # Parse any hsi flags
    if len(hsi_flags) > 0:
        args.extend(hsi_flags.split(" "))

    args.append("chmod")

    if len(chmod_flags) > 0:
        args.extend(chmod_flags.split(" "))

    args.append(mod)
    args.append(target)
    output = hsi(*args)

    return output


def chgrp(group_name: str, target: str, hsi_flags: str = "", chgrp_flags: str = "") -> str:
    """ Function to change the group of a file or directory on HPSS

    Parameters
    ----------
    group_name : str
            The group to which ownership of the file/directory is to be set.

    target : str
            Full path of the target location of the file on HPSS.

    hsi_flags : str
            String of flags to send to hsi.

    chgrp_flags : str
            Flags to send to chgrp.  See "hsi chgrp -?" for more details.
    """

    args = []

    # Parse any hsi flags
    if len(hsi_flags) > 0:
        args.extend(hsi_flags.split(" "))

    args.append("chgrp")

    if len(chgrp_flags) > 0:
        args.extend(chgrp_flags.split(" "))

    args.append(group_name)
    args.append(target)
    output = hsi(*args)

    return output


def rm(target: str, hsi_flags: str = "", rm_flags: str = "") -> str:
    """ Function to delete a file or directory on HPSS via hsi

    Parameters
    ----------
    target : str
            Full path of the target location of the file on HPSS.

    hsi_flags : str
            String of flags to send to hsi.

    rm_flags : str
            Flags to send to rm.  See "hsi rm -?" for more details.
    """

    args = []

    # Parse any hsi flags
    if len(hsi_flags) > 0:
        args.extend(hsi_flags.split(" "))

    args.append("rm")

    if len(rm_flags) > 0:
        args.extend(rm_flags.split(" "))

    args.append(target)
    output = hsi(*args)

    return output


def mkdir(target: str, hsi_flags: str = "", mkdir_flags: str = "") -> str:
    """ Function to delete a file or directory on HPSS via hsi

    Parameters
    ----------
    target : str
            Full path of the target location of the file on HPSS.

    hsi_flags : str
            String of flags to send to hsi.

    mkdir_flags : str
            Flags to send to mkdir (-p is assumed).  See "hsi mkdir -?" for more details.
    """

    args = []

    # Parse any hsi flags
    if len(hsi_flags) > 0:
        args.extend(hsi_flags.split(" "))

    args.extend(["mkdir", "-p"])

    if len(mkdir_flags) > 0:
        args.extend(mkdir_flags.split(" "))

    args.append(target)
    output = hsi(*args)

    return output


def ls(target: str, hsi_flags: str = "", ls_flags: str = "") -> str:
    """ Function to list files/directories on HPSS via hsi

    Parameters
    ----------
    target : str
            Full path of the target location on HPSS.

    hsi_flags : str
            String of flags to send to hsi.

    ls_flags : str
            Flags to send to ls.  See "hsi ls -?" for more details.
    """

    args = []

    # Parse any hsi flags
    if len(hsi_flags) > 0:
        args.extend(hsi_flags.split(" "))

    args.append("ls")

    if len(ls_flags) > 0:
        args.extend(ls_flags.split(" "))

    args.append(target)
    output = hsi(*args)

    return output


def exists(target: str) -> bool:
    """ Function to test the existence of a file/directory/glob on HPSS

    Parameters
    ----------
    target : str
            Full path of the target location on HPSS.

    Return: bool
            True if the target exists on HPSS.
    """

    cmd = which("hsi", required = True)

    for arg in ["ls", target]:
        cmd.add_default_arg(arg)

    # Do not exit if the file is not found; do not pipe output to stdout
    output = cmd(output = str, error = str, ignore_errors=[64])

    if "HPSS_ENOENT" in output:
        return False
    # Catch wildcards
    elif f"Warning: No matching names located for '{target}'" in output:
        return False
    else:
        return True
