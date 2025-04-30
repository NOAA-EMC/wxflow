import os
import tempfile

import pytest

from wxflow.utils import find_upward


@pytest.fixture
def temp_dir_structure():
    # Create a temporary directory structure for testing
    temp_dir = tempfile.TemporaryDirectory()
    root_dir = temp_dir.name
    sub_dir = os.path.join(root_dir, "subdir")
    target_file = os.path.join(root_dir, "target.txt")
    target_dir = os.path.join(root_dir, "target_dir")

    os.mkdir(sub_dir)
    with open(target_file, "w") as f:
        f.write("test")
    os.mkdir(target_dir)

    yield {
        "temp_dir": temp_dir,
        "root_dir": root_dir,
        "sub_dir": sub_dir,
        "target_file": target_file,
        "target_dir": target_dir,
    }

    # Clean up the temporary directory
    temp_dir.cleanup()


def test_find_upward_not_found(temp_dir_structure):
    # Test when the target is not found
    result = find_upward("nonexistent.txt", start_path=temp_dir_structure["sub_dir"])
    assert result is None


def test_find_upward_start_path_none(mocker):
    # Mock os.getcwd to return a specific directory
    mock_getcwd = mocker.patch("os.getcwd", return_value="/mocked/current/directory")

    # Call the function with start_path as None
    result = find_upward("some_target", start_path=None)

    # Assert that os.getcwd was called
    mock_getcwd.assert_called_once()

    # Assert the result is None since the mocked directory does not contain the target
    assert result is None


def test_find_upward_returns_correct_path(temp_dir_structure):
    # Test that the function returns the correct path to the target
    result = find_upward("target.txt", start_path=temp_dir_structure["sub_dir"])
    assert result == temp_dir_structure["root_dir"]


def test_find_upward_handles_symlinks(temp_dir_structure):
    # Create a symlink to the target file
    symlink_path = os.path.join(temp_dir_structure["sub_dir"], "symlink_to_target.txt")
    os.symlink(temp_dir_structure["target_file"], symlink_path)

    # Test finding the symlink
    result = find_upward("symlink_to_target.txt", start_path=temp_dir_structure["sub_dir"])
    assert result == temp_dir_structure["sub_dir"]

    # Clean up the symlink
    os.remove(symlink_path)


def test_find_upward_with_absolute_start_path(temp_dir_structure):
    # Test finding the target with an absolute start path
    result = find_upward("target.txt", start_path=os.path.abspath(temp_dir_structure["sub_dir"]))
    assert result == temp_dir_structure["root_dir"]


def test_find_upward_with_nonexistent_start_path():
    # Test with a nonexistent start path
    result = find_upward("target.txt", start_path="/nonexistent/path")
    assert result is None
