import os
import random
import string
from pathlib import Path

import pytest

from wxflow import CommandNotFoundError, Hsi, Htar

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
test_path = f'/NCEPDEV/emc-global/1year/{user}/htar_test/test-{test_hash}'


@pytest.mark.skipif(not htar, reason="Did not find the htar command")
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
    # Create files to send
    in_tmp_files = [input_dir_path / 'a.txt', input_dir_path / 'b.txt']
    for f in in_tmp_files:
        f.touch()
        f.write_text("Some contents")

    # Create a symlink, add it to tmp_files
    os.symlink("a.txt", input_dir_path / "ln_a.txt")
    in_tmp_files.append(input_dir_path / "ln_a.txt")

    test_tarball = test_path + "/test.tar"

    # Create the archive file
    output = htar.cvf(test_tarball, in_tmp_files, dereference=True)

    assert "a.txt" in output
    assert hsi.exists(test_tarball)

    # Extract the test archive
    output = htar.xvf(test_tarball, in_tmp_files)

    assert "a.txt" in output
    assert "ln_a.txt" in output

    # List the contents of the test archive
    output = htar.tell(test_tarball)

    assert "a.txt" in output

    # Remove the test directory
    output = hsi.rm(test_tarball)
    output = hsi.rm(test_tarball + ".idx")
    output = hsi.rmdir(test_path)
