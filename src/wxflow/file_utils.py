from logging import getLogger

from .fsutils import cp, mkdir, hsi_put, hsi_get, hsi_chmod, hsi_chgrp

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
    "action" can be one of mkdir", "copy", etc.
    Corresponding "act" would be ['dir1', 'dir2'], [['src1', 'dest1'], ['src2', 'dest2']]

    Attributes
    ----------
    config : dict
            Dictionary of files to manipulate
    """

    def __init__(self, config):

        self.config = config

    def sync(self):
        """
        Method to execute bulk actions on files described in the configuration
        """
        sync_factory = {
            'copy': self._copy_files,
            'mkdir': self._make_dirs,
        }
        # loop through the configuration keys
        for action, files in self.config.items():
            sync_factory[action](files)

    @staticmethod
    def _copy_files(filelist):
        """Function to copy all files specified in the list

        `filelist` should be in the form:
        - [src, dest]

        Parameters
        ----------
        filelist : list
                List of lists of [src, dest]
        """
        for sublist in filelist:
            if len(sublist) != 2:
                raise Exception(
                    f"List must be of the form ['src', 'dest'], not {sublist}")
            src = sublist[0]
            dest = sublist[1]
            cp(src, dest)
            logger.info(f'Copied {src} to {dest}')

    @staticmethod
    def _write_tarball(filelist, tarball):
        """Function to add all files specified in the list to the target tarball.
        The target tarball can have extensions .tar, .tar.bz2, .tar.gz, or .tgz,
        representing the desired compression.

        Parameters
        ----------
        filelist : list
                List of files

        tarball : str
                Name of the tarball to create/append to
        """

        # Check for valid tar extension
        valid_tar_extensions = [".tar", ".tar.gz", ".tgz", "tar.bz2"]
        valid = False

        for ext in valid_tar_extensions:
            if tarball.endswith(ext):
                valid = True

        if not valid:
            raise TypeError(f"Target tarball ({tarball}) has an invalid extension.")

        for file in filelist:
            # Check for globs
            write_tar(file, tarball)
            logger.info(f'Wrote {file} to {tarball}')

    @staticmethod
    def _make_dirs(dirlist):
        """Function to make all directories specified in the list

        Parameters
        ----------
        dirlist : list
                List of directories to create
        """
        for dd in dirlist:
            mkdir(dd)
            logger.info(f'Created {dd}')


class ArchiveHandler:
    """Class to interact with a target archive (e.g. .tar).  Presently, only
       archive creation is enabled.

    Parameters
    ----------
    config : dict
          A dictionary containing "protocol", "action", "target", and "fileset"

    NOTE
    ----
    "action" can be presently only be "create"
    "protocol" can be either "tar" or "htar"
    "target" is the name of the archive to act on
    "fileset" is a list of files to add to the archive
    "verbose" is an optional boolean key for extra output

    Attributes
    ----------
    config : dict
            Dictionary of files to manipulate
    """

    def __init__(self, config):

        self.config = config

    def create(self):
        """
        Method to create an archive based described in the configuration

        The input configuration should have the following keys
        protocol: str
                  Name of the archiving program (currently tar or htar)
        target: str
                  File name of the target archive
        fileset: list
                  List of files to write to the archive
        verbose: boolean (optional) 
                  Whether to print verbosely while writing or not
        """
        launcher = {
            'tar': self._create_tar,
            'htar': self._create_htar,
        }
        # Get configuration values
        protocol = self.config['protocol']
        target = self.config['target']
        fileset = self.config['fileset']
        action = self.config['action']
        verbose = False
        if "verbose" in self.config.keys():
            verbose = self.config['verbose']

        launcher[protocol] (target, fileset, verbose)

    @staticmethod
    def _create_tar(target, filelist, verbose=False):
        """Function to add all files specified in the list to the target tarball.
        The target tarball can have extensions .tar, .tar.bz2, .tar.gz, or .tgz,
        representing the desired compression.  This will overwrite an existing
        tar file.

        Parameters
        ----------
        target : str
                Name of the tarball to create

        filelist : list
                List of files

        verbose : boolean
                Whether to print as files are written to the tarball.
        """

        # Check for valid tar extension
        valid_tar_extensions = [".tar", ".tar.gz", ".tgz", "tar.bz2"]
        valid = False

        for ext in valid_tar_extensions:
            if target.endswith(ext):
                valid = True

        if not valid:
            raise TypeError(f"Target tarball {target} has an invalid extension.")

        # Create the parent directory if it does not yet exist
        if not os.path.exists(os.path.dirname(archive_name)):
            mkdir(os.path.dirname(archive_name))

        has_rstprod = False

        with tarfile.open(target) as handle:
            for file in fileset:
                if not has_rstprod:
                    if(os.stat(file).st_gid == gid_rstprod):
                        has_rstprod = True
                        os.chown(target, -1, gid_rstprod)
                        logger.info(f'Changed group of {target} to rstprod.')

                tar.add(file)
                write_tar(file, target)

    @staticmethod
    def _create_htar(target, filelist, verbose=False):
        """Function to add all files specified in the list to the target tarball
        on HPSS.  The target tarball may only have the extension .tar.  This will
        overwrite an existing tar file.

        Parameters
        ----------
        target : str
                Full path and filename of the tarball to create

        filelist : list
                List of files

        verbose : boolean
                Whether to print as files are written to the tarball.
        """

        # Check for valid tar extension
        if target.endswith(ext):
            valid = True

        if not target.endswith(".tar"):
            raise TypeError(f"Target tarball {target} has an invalid extension.")

        # Get the htar command.
        htar = which("htar", required=True)

        has_rstprod = False

        for file in fileset:
            if not has_rstprod:
                if(os.stat(file).st_gid == gid_rstprod):
                    has_rstprod = True

        # Build the htar command
        if verbose:
            htar.add_default_arg('-cvf')
        else:
            htar.add_default_arg('-cf')

        htar.add_default_arg(target)
        htar.add_default_arg(" ".join(filelist))

        # Attempt to run htar
        try:
            htar(output=str)
        except:
            if has_rstprod:
                # Attempt to change the group of the target file
                try:
                    hsi.chgrp("rstprod", target)
                    hsi.chmod("640", target)
                except:
                    hsi.rm(target, flags="-f")
                    raise OSError(f"Failed to change the group for a restricted data file.\n"
                                  f"Please verify that {target} was deleted!!")

            raise OSError(f"htar failed to archive {target}.")

        if has_rstprod:
            try:
                hsi.chgrp("rstprod", target)
                hsi.chmod("640", target)
            except:
                hsi.rm(target, flags="-f")
                raise OSError(f"Failed to change the group for a restricted data file.\n"
                              f"Please verify that {target} was deleted!!")
