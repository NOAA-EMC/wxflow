import os
import sys

import pytest

from wxflow import chdir, cp, get_gid, mkdir, rm_p, rmdir


def test_mkdir(tmp_path):
    """
    Test for creating a directory:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    dir_path = tmp_path / 'my_test_dir'
    dir_path_bad = "/some/non-existent/path"

    # Create the good path
    mkdir(dir_path)

    # Check if dir_path was created
    assert os.path.exists(dir_path)

    # Test that attempting to create a bad path raises an OSError
    with pytest.raises(OSError):
        mkdir(dir_path_bad)


def test_rmdir(tmp_path):
    """
    Test for removing a directory:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    dir_path = tmp_path / 'my_input_dir'
    # Make and then delete the directory
    mkdir(dir_path)
    rmdir(dir_path)

    # Assert that it was deleted
    assert not os.path.exists(dir_path)

    # Attempt to delete a non-existent path and ignore that it is missing
    rmdir('/non-existent-path', missing_ok=True)

    # Lastly, attempt to delete a non-existent directory and do not ignore the error
    with pytest.raises(FileNotFoundError):
        rmdir('/non-existent-path')


def test_chdir(tmp_path):
    """
    Test for changing a directory:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    dir_path = tmp_path / 'my_input_dir'
    # Make the directory and navigate to it
    mkdir(dir_path)

    # Get the CWD to verify that we come back after the with.
    cwd = os.getcwd()

    with chdir(dir_path):
        assert os.getcwd() == os.path.abspath(dir_path)

    assert os.getcwd() == cwd

    # Now try to go somewhere that doesn't exist
    with pytest.raises(OSError):
        with chdir("/a/non-existent/path"):
            raise AssertionError("Navigated to a non-existent path")

    # Lastly, test that we return to the orignial working directory when there is an error
    try:
        with chdir(dir_path):
            1 / 0
    except ZeroDivisionError:
        pass

    assert os.getcwd() == cwd


def test_rm_p(tmp_path):
    """
    Test for removing a file
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    input_path = tmp_path / 'my_test_file.txt'
    # Attempt to delete a non-existent file, ignoring any errors
    rm_p(input_path)

    # Now attempt to delete the same file but do not ignore errors
    with pytest.raises(FileNotFoundError):
        rm_p(input_path, missing_ok=False)

    with open(input_path, "w") as f:
        f.write("")

    # Delete the file and assert it doesn't exist
    rm_p(input_path)

    assert not os.path.isfile(input_path)


def test_cp(tmp_path):
    """
    Test copying a file:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    input_path = tmp_path / 'my_test_file.txt'
    output_path = tmp_path / 'my_output_file.txt'
    # Attempt to copy a non-existent file
    rm_p(input_path)  # Delete it if present
    with pytest.raises(OSError):
        cp(input_path, output_path)

    # Now create the input file and repeat
    with open(input_path, "w") as f:
        f.write("")

    cp(input_path, output_path)

    # Assert both files exist (make sure it wasn't moved).
    assert os.path.isfile(output_path)
    assert os.path.isfile(input_path)


def test_get_gid():
    """
    Test getting a group ID:
    """

    # Try to change groups to a non-existent one.
    with pytest.raises(KeyError):
        get_gid("some-non-existent-group")

    # Now get the group ID for root [0] (admin [80] on macOS)
    if sys.platform == 'darwin':
        assert get_gid("admin") == 80
    else:
        assert get_gid("root") == 0
