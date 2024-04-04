import os

from pathlib import Path

import pytest

import random

import string

from wxflow import Htar, Hsi, CommandNotFoundError

# These tests do not run on the GH runner as they it is not connected to HPSS.
# It is intended that these tests should only be run on Hera or WCOSS2.

try:
    htar = Htar()
    hsi = Hsi()
except CommandNotFoundError:
    hsi = None
    htar = None

test_hash = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
user = os.environ['USER']
test_path = f'/NCEPDEV/emc-global/1year/{user}/hsi_test/test-{test_hash}'


@pytest.mark.skipif(not htar, reason="Only runs on Hera/WCOSS2 with hpss module loaded.")
def test_htar():
    """
    Test for the htar command builder:
    """
    output = htar.htar(["-?"])

    assert type(output) is str
    assert "Usage" in output


@pytest.mark.skipif(not htar, reason="Only runs on Hera/WCOSS2 with hpss module loaded.")
def test_cvf_xvf_tell(tmp_path):
    """
    Test creating, extracting, and listing a tarball on HPSS:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    # Create temporary directories
    input_dir_path = tmp_path / 'my_input_dir'
    input_dir_path.mkdir()
    # Create an empty file to send
    in_tmp_file = input_dir_path / 'a.txt'
    in_tmp_file.touch()
    in_tmp_file.write_text("Contents of a.txt")

    test_tarball = test_path + "/test.tar"

    # Create the archive file
    output = htar.cvf(test_tarball, [str(in_tmp_file)])
    print("output::")
    print(output)

    assert "a.txt" in output
    assert hsi.exists(test_tarball)

    # Extract the test archive
    output = htar.xvf(test_tarball)

    assert "a.txt" in output

    # List the contents of the test archive
    output = htar.tell(test_tarball)

    assert "a.txt" in output

    # Remove the test directory
    output = hsi.rm(test_tarball)
    output = hsi.rm(test_tarball + ".idx")
    output = hsi.rmdir(test_path)
