import grp
import os
import shutil
import tempfile
from contextlib import contextmanager
from logging import getLogger

__all__ = ['mkdir', 'mkdir_p', 'rmdir', 'chdir', 'rm_p', 'cp', 'cpfs',
           'get_gid', 'chgrp']

logger = getLogger(__name__.split('.')[-1])


def mkdir_p(path):
    try:
        os.makedirs(path, exist_ok=True)
    except OSError:
        raise OSError(f"unable to create directory at {path}")


mkdir = mkdir_p


def rmdir(dir_path, missing_ok=False):
    """
    Attempt to delete a directory and all of its contents.
    If ignore_missing is True, then a missing directory will not raise an error.
    """

    try:
        shutil.rmtree(dir_path)

    except FileNotFoundError:
        if missing_ok:
            logger.warning(f"WARNING cannot remove the target path {dir_path} because it does not exist")
        else:
            raise FileNotFoundError(f"Target directory ({dir_path}) cannot be removed because it does not exist")

    except OSError:
        raise OSError(f"Unable to remove the target directory: {dir_path}")


@contextmanager
def chdir(path):
    """Change current working directory and yield.
    Upon completion, the working directory is switched back to the directory at the time of call.

    Parameters
    ----------
    path : str | os.PathLike
        Directory to change to for operations

    Example
    -------
    with chdir(path_to_cd_and_do_stuff):
        do_thing_1
        do_thing_2
    """
    cwd = os.getcwd()
    # Try to change paths.
    try:
        os.chdir(path)
    except OSError:
        raise OSError(f"Failed to change directory to ({path})")

    # If successful, yield to the calling "with" statement.
    try:
        yield
    finally:
        # Once the with is complete, head back to the original working directory
        os.chdir(cwd)


def rm_p(path, missing_ok=True):
    """
    Attempt to delete a file.
    If missing_ok is True, an error is not raised if the file does not exist.
    """

    try:
        os.unlink(path)
    except FileNotFoundError:
        if missing_ok:
            logger.warning(f"WARNING cannot remove the file {path} because it does not exist")
        else:
            raise FileNotFoundError(f"The file {path} does not exist")
    except OSError:
        raise OSError(f"unable to remove {path}")


def cp(source: str, target: str) -> None:
    """
    copy `source` file to `target` using `shutil.copyfile`
    If `target` is a directory, then the filename from `source` is retained into the `target`
    Parameters
    ----------
        source : str
                 Source filename
        target : str
                 Destination filename or directory
    Returns
    -------
        None
    """

    if os.path.isdir(target):
        target = os.path.join(target, os.path.basename(source))

    try:
        shutil.copy2(source, target)
    except OSError:
        raise OSError(f"Unable to copy {source} to {target}")
    except Exception as ee:
        logger.exception(f"An unknown error occurred while copying {source} to {target}")
        raise ee


def cpfs(source: str, target: str) -> None:
    """
    Safely copy ``source`` to ``target`` by first writing to a temporary file in
    the destination folder, fsync'ing it to durable storage, and then atomically
    renaming it onto the final target (overwriting any existing file).

    This mirrors the behavior of the ``prod_util`` ``cpfs`` utility used when
    staging files from ``DATA`` to ``COM``.  If ``target`` is a directory, the
    basename of ``source`` is retained (matching :func:`cp`).

    Parameters
    ----------
        source : str
                 Source filename
        target : str
                 Destination filename or directory

    Returns
    -------
        None
    """

    # Match cp() semantics for directory targets.
    if os.path.isdir(target):
        target = os.path.join(target, os.path.basename(source))

    dest_dir = os.path.dirname(target) or '.'
    if not os.path.isdir(dest_dir):
        raise OSError(f"Destination directory {dest_dir} does not exist")

    # Create a uniquely-named temporary file in the destination directory so the
    # subsequent rename is atomic on the same filesystem.
    try:
        fd, tmp_path = tempfile.mkstemp(prefix=f".{os.path.basename(target)}.",
                                        suffix='.tmp', dir=dest_dir)
        os.close(fd)
    except OSError:
        raise OSError(f"Unable to create temporary file in {dest_dir}")

    try:
        # Reuse cp() for the copy so metadata is preserved consistently.
        cp(source, tmp_path)

        # Force the temp file's data to durable storage before the rename.
        try:
            with open(tmp_path, 'rb') as fh:
                os.fsync(fh.fileno())
        except OSError:
            raise OSError(f"Unable to fsync temporary file {tmp_path}")

        # Atomic rename (overwrites target if it exists).
        try:
            os.replace(tmp_path, target)
        except OSError:
            raise OSError(f"Unable to move {tmp_path} to {target}")
    except Exception:
        # Clean up the temp file on any failure so we don't leave debris behind.
        rm_p(tmp_path, missing_ok=True)
        raise


# Group ID number for a given group name
def get_gid(group_name: str):
    try:
        group_id = grp.getgrnam(group_name).gr_gid
    except KeyError:
        raise KeyError(f"{group_name} is not a valid group name.")

    return group_id


# Change the group of a target file or directory
def chgrp(group_name, target, recursive=False):
    # TODO add recursive option
    gid = get_gid(group_name)
    uid = os.stat(target).st_uid
    os.chown(target, uid, gid)
