from .files import file_factory

__all__ = ['FileSystem']


class FileSystem:
    default_protocol = 'file'

    @classmethod
    def copy(cls, source: str, target: str) -> None:
        """
        Copies a file from source to destinations, both source and target
        need to be prefixed: file:// or s3://
        Parameters
        ----------
        source: str
            source file
        target: str
            target file

        Returns
        -------
        None
        """
        copier, source, target = cls._create_copier(source, target)
        copier.copy(source, target)

    @classmethod
    def copy_tree(cls, source: str, target: str) -> None:
        """
        Copies a full tree of directories / files
        Parameters
        ----------
        source: str
            source directory
        target: str
            target directory

        Returns
        -------
        None
        """
        copier, source, target = cls._create_copier(source, target)
        copier.copy_tree(source, target)

    @staticmethod
    def protocol_path(path: str) -> tuple:
        """
        In a string protocol://path, returns protocol and path separately
        Parameters
        ----------
        path: str
            string with protocol://path

        Returns
        -------
        tuple
            protocol: str, path: str
        """
        parts = path.split('://')
        if len(parts) == 1:
            parts = ['file', parts[0]]
        return parts[0], parts[1]

    @staticmethod
    def add_prefix(path, protocol):
        """
        prepends protocol:// to the string path

        Parameters
        ----------
        path: str
            string with path
        protocol: str
            protocol to prepend

        Returns
        -------
        protocol_path: str
            protocol://path
        """
        parts = path.split('://')
        if len(parts) == 1:
            path = '://'.join((protocol, path))
        return path

    @classmethod
    def add_default_prefix(cls, path):
        """
            prepends the default prefix to the string path
        """
        parts = path.split('://')
        if len(parts) == 1:
            # assume it's a local file
            path = '://'.join((cls.default_protocol, path))
        return path

    @classmethod
    def _create_copier(cls, source, target):
        # if the files don't have a protocol (protocol://) we add a default one: file://
        source = cls.add_default_prefix(source)
        target = cls.add_default_prefix(target)
        source_prefix, source_path = cls.protocol_path(source)
        target_prefix, target_path = cls.protocol_path(target)
        try:
            copier = file_factory.create(source_prefix + '_' + target_prefix)
        except IndexError:
            raise ValueError(f'Unknown protocol or typo in either {source} or {target}')
        else:
            return copier, source_path, target_path
