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


def test_copy_parallel_basic(tmp_path):
    """
    Test basic parallel copy functionality
    Parameters
    ----------
    tmp_path - pytest fixture
    """
    # Create input directory and files
    input_dir_path = tmp_path / 'parallel_input'
    config = {'mkdir': [input_dir_path]}
    FileHandler(config).sync()

    # Create multiple test files with some content
    src_files = []
    for i in range(10):
        src_file = input_dir_path / f'file_{i}.txt'
        src_file.write_text(f'Content of file {i}\n' * 100)
        src_files.append(src_file)

    # Create output directory
    output_dir_path = tmp_path / 'parallel_output'
    config = {'mkdir': [output_dir_path]}
    FileHandler(config).sync()

    # Create copy list
    copy_list = []
    dest_files = []
    for i, src in enumerate(src_files):
        dest = output_dir_path / f'file_{i}.txt'
        copy_list.append([src, dest])
        dest_files.append(dest)

    # Perform parallel copy
    FileHandler.copy_parallel(copy_list)

    # Verify all files were copied
    for src, dest in zip(src_files, dest_files):
        assert os.path.isfile(dest), f"Destination file {dest} does not exist"
        # Verify content matches
        assert src.read_text() == dest.read_text(), f"Content mismatch for {dest}"


def test_copy_parallel_with_num_processes(tmp_path):
    """
    Test parallel copy with specific number of processes
    Parameters
    ----------
    tmp_path - pytest fixture
    """
    # Create input directory and files
    input_dir_path = tmp_path / 'parallel_input'
    config = {'mkdir': [input_dir_path]}
    FileHandler(config).sync()

    # Create test files
    src_files = []
    for i in range(5):
        src_file = input_dir_path / f'file_{i}.txt'
        src_file.write_text(f'Content {i}')
        src_files.append(src_file)

    # Create output directory
    output_dir_path = tmp_path / 'parallel_output'
    config = {'mkdir': [output_dir_path]}
    FileHandler(config).sync()

    # Create copy list
    copy_list = []
    for i, src in enumerate(src_files):
        dest = output_dir_path / f'file_{i}.txt'
        copy_list.append([src, dest])

    # Perform parallel copy with 2 processes
    FileHandler.copy_parallel(copy_list, num_processes=2)

    # Verify all files were copied
    for i, src in enumerate(src_files):
        dest = output_dir_path / f'file_{i}.txt'
        assert os.path.isfile(dest)
        assert src.read_text() == dest.read_text()


def test_copy_parallel_error_propagation(tmp_path):
    """
    Test that errors in one copy cause the parent call to fail
    Parameters
    ----------
    tmp_path - pytest fixture
    """
    # Create input directory and files
    input_dir_path = tmp_path / 'parallel_input'
    config = {'mkdir': [input_dir_path]}
    FileHandler(config).sync()

    # Create valid source files
    src_files = []
    for i in range(3):
        src_file = input_dir_path / f'file_{i}.txt'
        src_file.write_text(f'Content {i}')
        src_files.append(src_file)

    # Create copy list with bad destination (unwritable directory)
    copy_list = []
    for i, src in enumerate(src_files):
        # Try to copy to an invalid location
        dest = "/dev/null/invalid_path.txt"
        copy_list.append([src, dest])

    # Attempt parallel copy - should fail
    with pytest.raises(OSError):
        FileHandler.copy_parallel(copy_list)


def test_copy_parallel_missing_required_file(tmp_path):
    """
    Test that missing required source files cause the parent call to fail
    Parameters
    ----------
    tmp_path - pytest fixture
    """
    # Create input directory
    input_dir_path = tmp_path / 'parallel_input'
    config = {'mkdir': [input_dir_path]}
    FileHandler(config).sync()

    # Create one valid file and reference one that doesn't exist
    valid_file = input_dir_path / 'valid.txt'
    valid_file.write_text('Valid content')
    missing_file = input_dir_path / 'missing.txt'

    # Create output directory
    output_dir_path = tmp_path / 'parallel_output'
    config = {'mkdir': [output_dir_path]}
    FileHandler(config).sync()

    # Create copy list with missing file
    copy_list = [
        [valid_file, output_dir_path / 'valid.txt'],
        [missing_file, output_dir_path / 'missing.txt']
    ]

    # Attempt parallel copy - should fail due to missing file
    with pytest.raises(FileNotFoundError, match=f"Source file '{missing_file}' does not exist"):
        FileHandler.copy_parallel(copy_list)


def test_copy_parallel_file_integrity(tmp_path):
    """
    Test that parallel copies are identical to their sources
    Parameters
    ----------
    tmp_path - pytest fixture
    """
    import hashlib

    # Create input directory
    input_dir_path = tmp_path / 'parallel_input'
    config = {'mkdir': [input_dir_path]}
    FileHandler(config).sync()

    # Create files with larger content to ensure integrity
    src_files = []
    src_hashes = []
    for i in range(5):
        src_file = input_dir_path / f'file_{i}.txt'
        # Create larger content
        content = f'Line {i}\n' * 10000
        src_file.write_text(content)
        src_files.append(src_file)
        # Calculate hash
        hash_obj = hashlib.sha256()
        hash_obj.update(content.encode())
        src_hashes.append(hash_obj.hexdigest())

    # Create output directory
    output_dir_path = tmp_path / 'parallel_output'
    config = {'mkdir': [output_dir_path]}
    FileHandler(config).sync()

    # Create copy list
    copy_list = []
    dest_files = []
    for i, src in enumerate(src_files):
        dest = output_dir_path / f'file_{i}.txt'
        copy_list.append([src, dest])
        dest_files.append(dest)

    # Perform parallel copy
    FileHandler.copy_parallel(copy_list)

    # Verify file integrity using hashes
    for i, dest in enumerate(dest_files):
        assert os.path.isfile(dest)
        content = dest.read_text()
        hash_obj = hashlib.sha256()
        hash_obj.update(content.encode())
        dest_hash = hash_obj.hexdigest()
        assert dest_hash == src_hashes[i], f"Hash mismatch for {dest}"


def test_copy_parallel_invalid_format(tmp_path):
    """
    Test that invalid copy list format raises appropriate error
    Parameters
    ----------
    tmp_path - pytest fixture
    """
    # Create a copy list with invalid format
    bad_copy_list = [['only_one_item']]

    # Attempt parallel copy with bad format - should fail
    with pytest.raises(IndexError, match="List must be of the form"):
        FileHandler.copy_parallel(bad_copy_list)
