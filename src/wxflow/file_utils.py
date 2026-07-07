import os
import tempfile
from logging import getLogger
from pathlib import Path

from .fsutils import cp, mkdir, rm_p

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
    "copy", "copy_req", "copy_opt", "copy_safe",
    "link", "link_req", "link_opt", etc.
    Corresponding "act" would be ['dir1', 'dir2'], [['src1', 'dest1'], ['src2', 'dest2']]
    "copy_req" will raise an error if the source file does not exist
    "copy_opt" will not raise an error if the source file does not exist but will present a warning
    "copy_safe" behaves like ``copy_req`` but copies via a temporary file that is fsync'd
    and then atomically renamed onto the destination (mirrors prod_util ``cpfs``)

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
            'copy_safe': self.copy_safe,
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
    def copy_safe(filelist):
        FileHandler._copy_files(filelist, required=True, copy_fn=FileHandler._safe_cp)

    @staticmethod
    def _safe_cp(source, target):
        """Copy ``source`` to ``target`` via a fsync'd temporary file that is
        atomically renamed onto the destination (mirrors prod_util ``cpfs``).

        Directory targets are handled like :func:`fsutils.cp` — the basename of
        ``source`` is retained.
        """
        if os.path.isdir(target):
            target = os.path.join(target, os.path.basename(source))

        dest_dir = os.path.dirname(target) or '.'
        if not os.path.isdir(dest_dir):
            raise OSError(f"Destination directory {dest_dir} does not exist")

        # Temp file in the destination directory keeps the rename atomic (same fs).
        try:
            fd, tmp_path = tempfile.mkstemp(prefix=f".{os.path.basename(target)}.",
                                            suffix='.tmp', dir=dest_dir)
            os.close(fd)
        except OSError:
            raise OSError(f"Unable to create temporary file in {dest_dir}")

        try:
            # Reuse cp() so metadata handling stays consistent with copy_req/copy_opt.
            cp(source, tmp_path)

            # Force the temp file's data to durable storage before the rename.
            try:
                with open(tmp_path, 'rb') as fh:
                    os.fsync(fh.fileno())
            except OSError:
                raise OSError(f"Unable to fsync temporary file {tmp_path}")

            # Atomic rename; overwrites target if it exists.
            try:
                os.replace(tmp_path, target)
            except OSError:
                raise OSError(f"Unable to move {tmp_path} to {target}")
        except Exception:
            rm_p(tmp_path, missing_ok=True)
            raise

    @staticmethod
    def _copy_files(filelist, required=True, copy_fn=cp):
        """Function to copy all files specified in the list

        `filelist` should be in the form:
        - [src, dest]

        Parameters
        ----------
        filelist : list
                List of lists of [src, dest]
        required : bool, optional
                Flag to indicate if the src file is required to exist. Default is True
        copy_fn : callable, optional
                Function used to perform the individual copy, called as ``copy_fn(src, dest)``.
                Defaults to :func:`fsutils.cp`; use :func:`fsutils.cpfs` for a fsync + atomic
                rename copy.
        """
        for sublist in filelist:
            if len(sublist) != 2:
                raise IndexError(
                    f"List must be of the form ['src', 'dest'], not {sublist}")
            src = sublist[0]
            dest = sublist[1]
            if os.path.exists(src):
                try:
                    copy_fn(src, dest)
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
