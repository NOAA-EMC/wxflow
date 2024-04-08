import os
import random
import string
from pathlib import Path

import pytest

from wxflow import CommandNotFoundError, Hsi

# These tests do not run on the GH runner as they it is not connected to HPSS.
# It is intended that these tests should only be run on Hera or WCOSS2.
# This test also assumes that you are a member of rstprod on HPSS.  If not,
# then the test_chgrp test will fail.

try:
    hsi = Hsi()
except CommandNotFoundError:
    hsi = None

test_hash = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
user = os.environ['USER']
test_path = f'/NCEPDEV/emc-global/1year/{user}/hsi_test/test-{test_hash}'


@pytest.mark.skipif(not hsi, reason="Did not find the hsi command")
def test_exists():
    """
    Test for checking if a target exists on HPSS
    """
    assert hsi.exists("/NCEPDEV")
    assert not hsi.exists("/not_a_file")


@pytest.mark.skipif(not hsi, reason="Did not find the hsi command")
def test_ls():
    """
    Test HPSS listing
    """
    output = hsi.ls("/NCEPDEV/")
    assert "emc-global" in output

    output = hsi.ls("/NCEPDEV/", ls_opts="-l")
    assert "drwxr-xr-x" in output


@pytest.mark.skipif(not hsi, reason="Did not find the hsi command")
def test_mkdir_rmdir():
    """
    Test for creating a directory:
    """

    # Create the test_path
    output = hsi.mkdir(test_path)

    # Check that the test path was created
    assert hsi.exists(test_path)

    # Remove the test_path
    output = hsi.rmdir(test_path)

    # Check that the test path was removed
    assert not hsi.exists(test_path)


@pytest.mark.skipif(not hsi, reason="Did not find the hsi command")
def test_chmod():
    """
    Test for chmod:
    """

    # Create the test_path
    output = hsi.mkdir(test_path)

    # Change the mode of the test path
    output = hsi.chmod("750", test_path, chmod_opts="-R")

    # Check that the mode was changed
    output = hsi.ls(test_path, ls_opts="-d -l")

    assert "drwxr-x---" in output

    # Remove the test_path
    output = hsi.rmdir(test_path)


@pytest.mark.skipif(not hsi, reason="Did not find the hsi command")
def test_chgrp():
    """
    Test for chgrp:
    """

    # Create the test_path
    output = hsi.mkdir(test_path)

    # Change the group of the test path
    output = hsi.chgrp("rstprod", test_path, chgrp_opts="-R")

    # Check that the group was changed
    output = hsi.ls(test_path, ls_opts="-d -l")

    assert "rstprod" in output

    # Remove the test_path
    output = hsi.rmdir(test_path)


@pytest.mark.skipif(not hsi, reason="Did not find the hsi command")
def test_put_get(tmp_path):
    """
    Test for sending/getting a file to/from HPSS:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    # Create temporary directories
    input_dir_path = tmp_path / 'my_input_dir'
    input_dir_path.mkdir()
    output_dir_path = tmp_path / 'my_output_dir'
    output_dir_path.mkdir()
    # Create an empty file to send
    in_tmp_file = input_dir_path / 'a.txt'
    in_tmp_file.touch()

    # Name the output file
    out_tmp_file = output_dir_path / 'a.txt'

    # Create test_path if it doesn't exist
    if not hsi.exists(test_path):
        hsi.mkdir(test_path)

    # Send the temporary file
    output = hsi.put(in_tmp_file, test_path + "/a.txt")

    assert "a.txt" in output
    assert hsi.exists(test_path + "/a.txt")

    # Get the temporary file
    output = hsi.get(test_path + "/a.txt", out_tmp_file)

    assert "a.txt" in output
    assert out_tmp_file.exists()

    # Remove the test directory
    output = hsi.rm(test_path + "/a.txt")
    output = hsi.rmdir(test_path)
