import pytest

from wxflow import FileSystem
from wxflow.files import FileFile


@pytest.fixture
def create_local_files(tmp_path):
    """Create temporary files for testing"""
    source_dir_path = tmp_path / 'source_dir'
    source_dir_path.mkdir()
    src_files = [source_dir_path / 'a.txt', source_dir_path / 'b.txt']
    for ff in src_files:
        ff.touch()


def test_copy(tmp_path, create_local_files):
    source = tmp_path / 'source_dir' / 'a.txt'
    target = tmp_path / 'target_dir' / 'a_copy.txt'
    FileSystem.copy(str(source), str(target))
    assert target.exists()


def test_protocol_path(tmp_path):
    file_path = 'file://' + str(tmp_path / 'a.txt')
    assert FileSystem.protocol_path(file_path) == ('file', str(tmp_path / 'a.txt'))


def test_add_prefix(tmp_path):
    file_path = tmp_path / 'a.txt'
    assert FileSystem.add_prefix(str(file_path), 's3') == 's3://' + str(file_path)


def test_add_default_prefix(tmp_path):
    file_path = tmp_path / 'a.txt'
    assert FileSystem.add_default_prefix(str(file_path)) == 'file://' + str(file_path)


def test_local_create_copier(tmp_path):
    source = tmp_path / 'source_dir' / 'a.txt'
    target = tmp_path / 'target_dir' / 'a.txt'
    copier, source_path, target_path = FileSystem._create_copier(str(source), str(target))
    assert isinstance(copier, FileFile)
    assert source_path == str(source_path)
    assert target_path == str(target_path)
