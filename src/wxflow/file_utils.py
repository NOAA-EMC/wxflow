import os
from logging import getLogger
from multiprocessing import Pool
from pathlib import Path

from .fsutils import cp, mkdir

__all__ = ['FileHandler']

logger = getLogger(__name__.split('.')[-1])


def _copy_single_file(src, dest):
    """Helper function to copy a single file. Used by multiprocessing.Pool.

    Parameters
    ----------
    src : str
            Source file path
    dest : str
            Destination file path

    Returns
    -------
    tuple
            (success: bool, src: str, dest: str, error: Exception or None)
    """
    try:
        cp(src, dest)
        return (True, src, dest, None)
    except Exception as ee:
        return (False, src, dest, ee)


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
    def copy_parallel(filelist, num_processes=None):
        """Function to copy files in parallel using multiprocessing.Pool

        Parameters
        ----------
        filelist : list
                List of lists of [src, dest]
        num_processes : int, optional
                Number of processes to use for parallel copying.
                If None, uses the number of CPUs on the machine.
        """
        FileHandler._copy_files_parallel(filelist, required=True, num_processes=num_processes)

    @staticmethod
    def _copy_files_parallel(filelist, required=True, num_processes=None):
        """Function to copy files in parallel using multiprocessing.Pool

        `filelist` should be in the form:
        - [src, dest]

        Parameters
        ----------
        filelist : list
                List of lists of [src, dest]
        required : bool, optional
                Flag to indicate if the src file is required to exist. Default is True
        num_processes : int, optional
                Number of processes to use for parallel copying.
                If None, uses the number of CPUs on the machine.
        """
        # Validate filelist format
        for sublist in filelist:
            if len(sublist) != 2:
                raise IndexError(
                    f"List must be of the form ['src', 'dest'], not {sublist}")

        # Check that all required source files exist before starting any copies
        for sublist in filelist:
            src = sublist[0]
            if not os.path.exists(src):
                if required:
                    logger.exception(f"Source file '{src}' does not exist and is required, ABORT!")
                    raise FileNotFoundError(f"Source file '{src}' does not exist")
                else:
                    logger.warning(f"Source file '{src}' does not exist, skipping!")

        # Filter out files where source doesn't exist (for optional copies)
        valid_files = [sublist for sublist in filelist if os.path.exists(sublist[0])]

        if not valid_files:
            logger.warning("No valid files to copy")
            return

        # Use multiprocessing.Pool to copy files in parallel
        with Pool(processes=num_processes) as pool:
            results = pool.starmap(_copy_single_file, valid_files)

        # Check if any copies failed
        for i, (success, src, dest, error) in enumerate(results):
            if not success:
                logger.exception(f"Error copying {src} to {dest}: {error}")
                raise error
            else:
                logger.info(f'Copied {src} to {dest}')

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
