import os
import shutil
from logging import getLogger
from pathlib import Path

from .fsutils import cp, mkdir, mkdir_p

__all__ = ['FileHandler']

logger = getLogger(__name__.split('.')[-1])


class FileHandler:
    """Class to manipulate files in bulk for a given configuration

    Parameters
    ----------
    config : dict
          A dictionary containing the "action" and the "act" in the form of a list

    NOTE
    ----
    "action" can be one of:
    "mkdir",
    "copy", "copy_req", "copy_opt",
    "link", "link_req", "link_opt", etc.
    Corresponding "act" would be ['dir1', 'dir2'], [['src1', 'dest1'], ['src2', 'dest2']]
    "copy_req" will raise an error if the source file does not exist
    "copy_opt" will not raise an error if the source file does not exist but will present a warning

    Attributes
    ----------
    config : dict
            Dictionary of files to manipulate

    NOTE
    ----
    `copy` will be deprecated in the future in favor of `copy_req` and `copy_opt`
    Users are encouraged to use `copy_req` and `copy_opt` instead of `copy`
    `link` will be deprecated in the future in favor of `link_req` and `link_opt`
    Users are encouraged to use `link_req` and `link_opt` instead of `link`
    """

    def __init__(self, config):

        self.config = config

    def sync(self):
        """
        Method to execute bulk actions on files described in the configuration
        """
        sync_factory = {
            'mkdir': self._make_dirs,
            'copy': self.copy_req,
            'copy_req': self.copy_req,
            'copy_opt': self.copy_opt,
            'copy_req_dir': self.copy_req_dir,
            'link': self.link_opt,
            'link_req': self.link_req,
            'link_opt': self.link_opt
        }
        # loop through the configuration keys
        for action, files in self.config.items():
            if files is None or len(files) == 0:
                logger.warning(f"WARNING: No files/directories were included for {action} command")
                continue
            sync_factory[action](files)

    @staticmethod
    def copy_req(filelist):
        FileHandler._copy_files(filelist, required=True)

    @staticmethod
    def copy_opt(filelist):
        FileHandler._copy_files(filelist, required=False)

    @staticmethod
    def _copy_files(filelist, required=True):
        """Function to copy all files specified in the list

        `filelist` should be in the form:
        - [src, dest]

        Parameters
        ----------
        filelist : list
                List of lists of [src, dest]
        required : bool, optional
                Flag to indicate if the src file is required to exist. Default is True
        """
        for sublist in filelist:
            if len(sublist) != 2:
                raise IndexError(
                    f"List must be of the form ['src', 'dest'], not {sublist}")
            src = sublist[0]
            dest = sublist[1]
            if os.path.exists(src):
                try:
                    cp(src, dest)
                    logger.info(f'Copied {src} to {dest}')
                except Exception as ee:
                    logger.exception(f"Error copying {src} to {dest}")
                    raise ee
            else:
                if required:
                    logger.exception(f"Source file '{src}' does not exist and is required, ABORT!")
                    raise FileNotFoundError(f"Source file '{src}' does not exist")
                else:
                    logger.warning(f"Source file '{src}' does not exist, skipping!")

    @staticmethod
    def _make_dirs(dirlist):
        """Function to make all directories specified in the list

        Parameters
        ----------
        dirlist : list
                List of directories to create
        """
        for dd in dirlist:
            try:
                mkdir(dd)
                logger.info(f'Created {dd}')
            except Exception as ee:
                logger.exception(f"Error creating directory {dd}")
                raise ee

    @staticmethod
    def link_req(filelist):
        FileHandler._link_files(filelist, required=True)

    @staticmethod
    def link_opt(filelist):
        FileHandler._link_files(filelist, required=False)

    @staticmethod
    def _link_files(filelist, required=True):
        """Function to link all files specified in the list

        `filelist` should be in the form:
        - [target, link name]

        Parameters
        ----------
        filelist : list
                List of lists of [target, link name]
        required : bool, optional
                Flag to indicate if the target file is required to exist. Default is True
        """
        for sublist in filelist:
            if len(sublist) != 2:
                raise IndexError(
                    f"List must be of the form ['target', 'link name'], not {sublist}")
            target = sublist[0]
            link_name = sublist[1]
            if os.path.isdir(link_name):
                link_name = os.path.join(link_name, os.path.basename(target))
            if not os.path.exists(target):
                if required:
                    logger.exception(f"Target file '{target}' does not exist and is required, ABORT!")
                    raise FileNotFoundError(f"Target file '{target}' does not exist")
                else:
                    logger.warning(f"WARNING: Target file '{target}' does not exist, will result in dead link!")
            link_path = Path(link_name)
            if link_path.is_symlink():
                logger.warning(f"WARNING: Link to '{target}' exists at '{link_name}', removing!")
                os.remove(link_name)
            link_path.symlink_to(target)
            logger.info(f"Linked '{target}' to '{link_name}'")

    @staticmethod
    def copy_req_dir(filelist):
        """Copy each source to a destination directory, creating the directory if needed.

        A bulk dispatcher for ``_copy_file_to_dir``, following the same filelist
        convention as ``copy_req`` and ``copy_opt``. Each entry must be
        ``[src, dest_dir]`` or ``[src, dest_dir, is_dir]``. For each entry the
        destination directory is created (with ``mkdir -p`` semantics) if it does
        not already exist, then the source is copied into it.

        This method is wired into ``sync`` under the ``'copy_req_dir'`` action key,
        so it can be driven directly from a ``FileHandler`` configuration dict.

        Parameters
        ----------
        filelist : list
            List of entries of the form ``[src, dest_dir]`` or
            ``[src, dest_dir, is_dir]``.  ``is_dir`` defaults to False when
            omitted.

        Examples
        --------
        Via ``sync``:

        >>> fh = FileHandler({'copy_req_dir': [['input/file.nc', 'output/run1/'],
        ...                                    ['input/subdir', 'output/run1/', True]]})
        >>> fh.sync()

        Directly:

        >>> FileHandler.copy_req_dir([['input/file.nc', 'output/run1/']])
        """
        for entry in filelist:
            if len(entry) not in (2, 3):
                raise IndexError(
                    f"Entry must be ['src', 'dest_dir'] or ['src', 'dest_dir', is_dir], not {entry}")
            src = entry[0]
            dest_dir = entry[1]
            is_dir = entry[2] if len(entry) == 3 else False
            FileHandler._copy_file_to_dir(src, dest_dir, is_dir)

    @staticmethod
    def _copy_file_to_dir(src_path, target_dir, is_dir=False):
        """Safely copy a single file or directory to a destination, creating the destination directory if needed.

        This is a convenience utility that combines directory creation and copying
        into a single guarded operation. It validates that the source exists and is
        readable before attempting any filesystem changes, and automatically creates
        the destination directory (including any missing intermediate directories) if
        it does not already exist. The copy is then performed atomically with respect
        to the directory creation step.

        Use this method when the destination directory may not yet exist at the time
        of the copy, such as during workflow staging where output directories are
        created on demand.

        Parameters
        ----------
        src_path : str
            Path to the source file or directory to copy.
        target_dir : str
            Path to the destination directory. Created (with ``mkdir -p`` semantics)
            if it does not already exist.
        is_dir : bool, optional
            If True, treat ``src_path`` as a directory and copy recursively using
            ``shutil.copytree``. The directory is placed inside ``target_dir`` under
            its original base name. If False (default), treat ``src_path`` as a
            file and copy it into ``target_dir`` using ``shutil.copy2``, preserving
            metadata.

        Returns
        -------
        bool
            True if the source was successfully copied to ``target_dir``.
            False if the source does not exist, is not readable, the destination
            directory could not be created, or the copy itself failed. All failure
            cases are logged at ERROR level.

        Examples
        --------
        Copy a single file, creating the destination directory if absent:

        >>> FileHandler._copy_file_to_dir('/data/input/file.nc', '/data/output/run1/')

        Copy an entire directory tree into a destination:

        >>> FileHandler._copy_file_to_dir('/data/input/subdir', '/data/output/run1/', is_dir=True)
        """
        src_type = "directory" if is_dir else "file"
        valid = os.path.isdir(src_path) if is_dir else os.path.isfile(src_path)
        if not valid:
            logger.error(f"Source {src_type} '{src_path}' does not exist")
            return False
        if not os.access(src_path, os.R_OK):
            logger.error(f"Source {src_type} '{src_path}' is not readable")
            return False
        if not os.path.exists(target_dir):
            logger.info(f"Directory '{target_dir}' does not exist, creating...")
            try:
                mkdir_p(target_dir)
            except OSError:
                logger.error(f"Failed to create destination directory '{target_dir}'")
                return False
        try:
            if is_dir:
                target = os.path.join(target_dir, os.path.basename(src_path))
                shutil.copytree(src_path, target)
            else:
                shutil.copy2(src_path, target_dir)
        except OSError:
            logger.error(f"Failed to copy {src_type} '{src_path}' to '{target_dir}'")
            return False
        return True
