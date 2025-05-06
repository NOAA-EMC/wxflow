import logging
import os

import pytest

from wxflow import FileHandler


def test_mkdir(tmp_path):
    """
    Test for creating directories:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    dir_path = tmp_path / 'my_test_dir'
    d1 = f'{dir_path}1'
    d2 = f'{dir_path}2'
    d3 = f'{dir_path}3'

    # Create config object for FileHandler
    config = {'mkdir': [d1, d2, d3]}

    # Create d1, d2, d3
    FileHandler(config).sync()

    # Check if d1, d2, d3 were indeed created
    for dd in config['mkdir']:
        assert os.path.exists(dd)


def test_bad_mkdir():
    # Attempt to create a directory in an unwritable parent directory
    with pytest.raises(OSError):
        FileHandler({'mkdir': ["/dev/null/foo"]}).sync()


def test_empty_lists(caplog):
    caplog.set_level(logging.INFO)
    FileHandler({'mkdir': None}).sync()
    assert 'WARNING: No files/directories were included for mkdir command' in caplog.text
    FileHandler({'copy': []}).sync()
    assert 'WARNING: No files/directories were included for copy command' in caplog.text


def test_copy(tmp_path):
    """
    Test for copying files:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    # Test 1 (nominal operation) - Creating a directory and copying files to it
    input_dir_path = tmp_path / 'my_input_dir'

    # Create the input directory
    config = {'mkdir': [input_dir_path]}
    FileHandler(config).sync()

    # Put empty files in input_dir_path
    src_files = [input_dir_path / 'a.txt', input_dir_path / 'b.txt']
    for ff in src_files:
        ff.touch()

    # Create output_dir_path and expected file names
    output_dir_path = tmp_path / 'my_output_dir'
    config = {'mkdir': [output_dir_path]}
    FileHandler(config).sync()
    dest_files = [output_dir_path / 'a.txt', output_dir_path / 'bb.txt']

    copy_list = []
    for src, dest in zip(src_files, dest_files):
        copy_list.append([src, dest])

    # Create config dictionary for FileHandler
    config = {'copy': copy_list}

    # Copy input files to output files
    FileHandler(config).sync()

    # Check if files were indeed copied
    for ff in dest_files:
        assert os.path.isfile(ff)

    # Test 2 - Attempt to copy files to a non-writable directory
    # Create a list of bad targets (/dev/null is unwritable)
    bad_dest_files = ["/dev/null/a.txt", "/dev/null/bb.txt"]

    bad_copy_list = []
    for src, dest in zip(src_files, bad_dest_files):
        bad_copy_list.append([src, dest])

    # Create a config dictionary for FileHandler
    bad_config = {'copy': bad_copy_list}

    # Attempt to copy
    with pytest.raises(OSError):
        FileHandler(bad_config).sync()

    # Test 3 - Attempt to copy missing, optional files to a writable directory
    # Create a config dictionary (c.txt does not exist)
    copy_list.append([input_dir_path / 'c.txt', output_dir_path / 'c.txt'])
    config = {'copy_opt': copy_list}

    # Copy input files to output files (should not raise an error)
    FileHandler(config).sync()

    # Test 4 - Attempt to copy missing, required files to a writable directory
    # Create a config dictionary (c.txt does not exist)
    config = {'copy_req': copy_list}
    c_file = input_dir_path / 'c.txt'
    with pytest.raises(FileNotFoundError, match=f"Source file '{c_file}' does not exist"):
        FileHandler(config).sync()


@pytest.fixture
def create_dirs_and_files_for_test_link(tmp_path):
    """
    Create directories and files for testing linking files:
    Parameters
    ----------
    tmp_path - pytest fixture
    """

    input_dir_path = tmp_path / 'my_input_dir'

    # Create the input directory
    config = {'mkdir': [input_dir_path]}
    FileHandler(config).sync()

    # Put empty files in input_dir_path
    src_files = [input_dir_path / 'a.txt', input_dir_path / 'b.txt']
    for ff in src_files:
        ff.touch()

    # Create output_dir_path for this test
    output_dir_path1 = tmp_path / 'my_output_dir1'
    output_dir_path2 = tmp_path / 'my_output_dir2'
    config = {'mkdir': [output_dir_path1, output_dir_path2]}
    FileHandler(config).sync()


def test_link_file_invalid_config(tmp_path, create_dirs_and_files_for_test_link):
    """
    Test for linking files:
    Parameters
    ----------
    tmp_path - pytest fixture
    create_dirs_and_files_for_test_link - pytest fixture
    """

    input_dir_path = tmp_path / 'my_input_dir'
    output_dir_path = tmp_path / 'my_output_dir1'

    # Create config dictionary for FileHandler
    bad_config = {'link': [[input_dir_path / 'a.txt'], [input_dir_path / 'b.txt', output_dir_path / 'b_link.txt']]}

    # Attempt to link
    with pytest.raises(IndexError):
        FileHandler(bad_config).sync()


def test_link_file_files(tmp_path, create_dirs_and_files_for_test_link):
    """
    Test for linking files:
    Parameters
    ----------
    tmp_path - pytest fixture
    create_dirs_and_files_for_test_link - pytest fixture
    """

    input_dir_path = tmp_path / 'my_input_dir'
    output_dir_path = tmp_path / 'my_output_dir1'

    src_files = [input_dir_path / 'a.txt', input_dir_path / 'b.txt']
    link_files = [output_dir_path / 'a_link.txt', output_dir_path / 'b_link.txt']

    link_list = []
    for src, link in zip(src_files, link_files):
        link_list.append([src, link])
        if os.path.exists(link):
            os.unlink(link)

    # Create config dictionary for FileHandler
    config = {'link': link_list}

    # Link input files to output links
    FileHandler(config).sync()

    # Check if links were indeed created
    for link in link_files:
        assert os.path.islink(link)
        assert os.readlink(link) == str(src_files[link_files.index(link)])

    # Create link input files to output links again to ensure removal of existing link
    FileHandler(config).sync()

    # Check if links were indeed created
    for link in link_files:
        assert os.path.islink(link)
        assert os.readlink(link) == str(src_files[link_files.index(link)])


def test_link_file_dir(tmp_path, create_dirs_and_files_for_test_link):
    """
    Test for linking files:
    Parameters
    ----------
    tmp_path - pytest fixture
    create_dirs_and_files_for_test_link - pytest fixture
    """

    input_dir_path = tmp_path / 'my_input_dir'
    output_dir_path = tmp_path / 'my_output_dir2'

    src_files = [input_dir_path / 'a.txt', input_dir_path / 'b.txt']
    link_files = [str(output_dir_path) + '/', str(output_dir_path) + '/']

    link_list = []
    for src, link in zip(src_files, link_files):
        link_list.append([src, link])
        link_name = os.path.join(link, os.path.basename(src))
        if os.path.exists(link_name):
            os.unlink(link_name)

    # Create config dictionary for FileHandler
    config = {'link': link_list}

    # Link input files to output links
    FileHandler(config).sync()

    # Check if links were indeed created
    for src, link in zip(src_files, link_files):
        link_name = os.path.join(link, os.path.basename(src))
        assert os.path.islink(link_name)


def test_link_file_bad(tmp_path, create_dirs_and_files_for_test_link):
    """
    Test for linking files:
    Parameters
    ----------
    tmp_path - pytest fixture
    create_dirs_and_files_for_test_link - pytest fixture
    """

    input_dir_path = tmp_path / 'my_input_dir'
    output_dir_path = tmp_path / 'my_output_dir1'

    bad_link_list = [[input_dir_path / 'non_existent.txt', output_dir_path / 'bad_link.txt']]

    # Create a config dictionary for FileHandler
    bad_config = {'link': bad_link_list}
    FileHandler(bad_config).sync()

    # Follow the bad link to the file and check this is a dead link to a file that does not exist
    pp = os.path.realpath(output_dir_path / 'bad_link.txt')
    assert not os.path.isfile(pp)

    # Attempt to link a non-existent file that is required
    bad_config = {'link_req': bad_link_list}
    with pytest.raises(FileNotFoundError):
        FileHandler(bad_config).sync()
