import os

from ..fsutils import tree

try:
    from fsspec.implementations.local import LocalFileSystem
    use_fsspec = True
    _lfs = LocalFileSystem()
except ImportError:
    import shutil
    use_fsspec = False


class FileFile:

    @classmethod
    def copy(cls, source: str, target: str) -> None:
        if use_fsspec:
            cls.fsspec_copy(source, target)
        else:
            cls.os_copy(source, target)

    @classmethod
    def copy_tree(cls, source: str, target: str) -> None:
        cls.os_copy_tree(source, target)

    @staticmethod
    def os_copy(source: str, target: str) -> None:
        target_path = os.path.dirname(target)
        if len(target_path):
            os.makedirs(target_path, exist_ok=True)
        shutil.copy(source, target)

    @classmethod
    def os_copy_tree(cls, source, target):
        for source, path, file in tree(source):
            source_path = os.path.join(source, path, file)
            target_path = os.path.join(target, path, file)
            cls.copy(source_path, target_path)

    @staticmethod
    def fsspec_copy(source: str, target: str) -> None:
        target_path = os.path.dirname(target)
        if not _lfs.exists(target_path):
            _lfs.makedirs(target_path)
        _lfs.copy(source, target)
