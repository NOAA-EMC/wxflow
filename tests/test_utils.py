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


def test_find_upward_file(temp_dir_structure):
    # Test finding a file
    result = find_upward("target.txt", start_path=temp_dir_structure["sub_dir"])
    assert result == temp_dir_structure["target_file"]


def test_find_upward_directory(temp_dir_structure):
    # Test finding a directory
    result = find_upward("target_dir", start_path=temp_dir_structure["sub_dir"])
    assert result == temp_dir_structure["target_dir"]


def test_find_upward_not_found(temp_dir_structure):
    # Test when the target is not found
    result = find_upward("nonexistent.txt", start_path=temp_dir_structure["sub_dir"])
    assert result is None


def test_find_upward_from_root(temp_dir_structure):
    # Test starting from the root directory
    result = find_upward("target.txt", start_path=temp_dir_structure["root_dir"])
    assert result == temp_dir_structure["target_file"]


def test_find_upward_start_path_none(mocker):
    # Mock os.getcwd to return a specific directory
    mock_getcwd = mocker.patch("os.getcwd", return_value="/mocked/current/directory")

    # Call the function with start_path as None
    result = find_upward("some_target", start_path=None)

    # Assert that os.getcwd was called
    mock_getcwd.assert_called_once()

    # Assert the result is None since the mocked directory does not contain the target
    assert result is None
