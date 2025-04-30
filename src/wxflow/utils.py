import os

__all__ = ['find_upward']


def find_upward(target_name, start_path=None):
    """
    Walks up the directory tree from the given start_path (or current dir)
    in search of a file or directory with the specified name.

    Parameters:
        target_name (str): The name of the file or directory to search for.
        start_path (str, optional): The path to start searching from.
            Defaults to the current working directory.

    Returns:
        str or None: Absolute path to the directory of the found target, or None if not found.
    """
    if start_path is None:
        current_path = os.getcwd()
    else:
        current_path = os.path.abspath(start_path)

    while True:
        candidate_path = os.path.join(current_path, target_name)
        if os.path.exists(candidate_path):
            return os.path.abspath(current_path)

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path:
            # Reached the filesystem root
            break

        current_path = parent_path

    return None
