import grp
import os
import shutil
from contextlib import contextmanager
from logging import getLogger

__all__ = ['mkdir', 'mkdir_p', 'rmdir', 'chdir', 'rm_p', 'cp',
           'get_gid', 'chgrp', 'create_dir_before_copy']

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


def create_dir_before_copy(src_path, target_dir, is_dir=False):
    """Check if src_path is available to copy and create target_dir if it does not exist.

    Parameters
    ----------
    src_path : str
        Path to the source file or directory.
    target_dir : str
        Path to the target directory to create if it does not exist.
    is_dir : bool, optional
        If True, treat src_path as a directory. If False (default), treat as a file.

    Returns
    -------
    bool
        True if src_path exists, is readable, and target_dir is ready. False otherwise.
    """
    src_type = "directory" if is_dir else "file"
    valid = os.path.isdir(src_path) if is_dir else os.path.isfile(src_path)
    if not valid:
        logger.error(f"Source {src_type} '{src_path}' does not exist")
        return False
    if not os.access(src_path, os.R_OK):
        logger.error(f"Source {src_type} '{src_path}' is not readable")
        return False
    if not os.path.exists(target_dir):
        logger.info(f"Directory '{target_dir}' does not exist, creating...")
        try:
            mkdir_p(target_dir)
        except OSError:
            logger.error(f"Failed to create destination directory '{target_dir}'")
            return False
    return True


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
