import contextlib
import errno
import os
import shutil

__all__ = ['mkdir', 'mkdir_p', 'rmdir', 'chdir', 'rm_p', 'cp', 'tree']


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise OSError(f"unable to create directory at {path}")


mkdir = mkdir_p


def rmdir(dir_path):
    try:
        shutil.rmtree(dir_path)
    except OSError as exc:
        raise OSError(f"unable to remove {dir_path}")


@contextlib.contextmanager
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
    try:
        os.chdir(path)
        yield
    finally:
        print(f"WARNING: Unable to chdir({path})")  # TODO: use logging
        os.chdir(cwd)


def rm_p(path):
    try:
        os.unlink(path)
    except OSError as exc:
        if exc.errno == errno.ENOENT:
            pass
        else:
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
        raise OSError(f"unable to copy {source} to {target}")
    except Exception as exc:
        raise Exception(exc)


def tree(path):
    """
    Recursively visits path. Returns a tuple with three elements:
    path (argument to the function), relative path, filename
        To have the full_path:
        for root, path, filename in tree(root):
            full_path = os.path.join(root, path, filename)
    Parameters
    ----------
    path : str
        Path to recursively visit
    Returns
    -------
    tuple : (str, str, str)
        path (argument to the function), relative path, filename
    """
    for root, dirs, files in os.walk(path):
        if len(files):
            for file in files:
                rr = root.replace(path, '', 1)
                if len(rr) and rr[0] == '/':
                    rr = rr[1:]
                yield path, rr, file
