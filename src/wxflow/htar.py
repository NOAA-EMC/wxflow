from .executable import which

__all__ = ['Htar']


class Htar:
    """
    Class offering an interface to HPSS via the htar utility.

    Examples:
    --------

    >>> from wxflow import Htar
    >>> htar = Htar()  # Generates an Executable object of "htar"
    >>> output = htar.cvf("/HPSS/path/to/archive.tar", "file1 file2") # Create an HPSS archive from two local files
    >>> output = htar.tell("/HPSS/path/to/archive.tar") # List the contents of an archive
    """
    def __init__(self) -> None:
        self.exe = which("htar")

    def htar(self, args, silent: bool = False) -> str:
        """
        Direct command builder function for htar based on the input arguments.

        Parameters:
        -----------
        args: list
            List of string arguments to send to htar

        silent: bool
            Flag to suppress output to stdout

        Return: str
            Output from the htar command

        Examples:
        ---------
        >>> htar = Htar()
        >>> # Run `htar -cvf /path/to/hpss/archive.tar file1 file2 file-*
        >>> htar.htar("-cvf", "/path/to/hpss/archive.tar", "file1 file2 file-*")
        """

        if silent:
            output = self.exe(*args, output=str, error=str)
        else:
            output = self.exe(*args, output=str.split, error=str.split)

        return output

    def create(self, tarball: str, fileset: list, flags: str = "-P") -> str:
        """ Method to write an archive to HPSS

        Parameters
        ----------
        flags : str
                String of flags to send to htar.

        tarball : str
                Full path location on HPSS to create the archive.

        fileset : list
                List containing filenames, patterns, or directories to archive
        """
        args = ["-c"]

        # Parse any htar flags
        if len(flags) > 0:
            args += flags.split(" ")

        if len(fileset) == 0:
            raise ValueError("Input fileset is empty, cannot create archive")

        args += ["-f", tarball, ' '.join(fileset)]

        output = self.htar(args)

        return output

    def cvf(self, tarball: str, fileset: list) -> str:
        """ Method to write an archive to HPSS verbosely (without flags).

        Parameters
        ----------
        tarball : str
                Full path location on HPSS to create the archive.

        fileset : list
                List containing filenames, patterns, or directories to archive
        """
        output = self.create(tarball, fileset, flags="-v -P")

        return output

    def extract(self, tarball: str, fileset: list = [], flags: str = "") -> str:
        """ Method to extract an archive from HPSS via htar

        Parameters
        ----------
        flags : str
                String of flags to send to htar.

        tarball : str
                Full path location of an archive on HPSS to extract from.

        fileset : list
                List containing filenames, patterns, or directories to extract from
                the archive.  If empty, then all files will be extracted.
        """
        args = ["-x"]

        # Parse any htar flags
        if len(flags) > 0:
            args += flags.split(" ")

        args += ["-f", tarball]

        if len(fileset) > 0:
            args.append(' '.join(fileset))

        output = self.htar(args)

        return output

    def xvf(self, tarball: str = "", fileset: list = []) -> str:
        """ Method to extract an archive from HPSS verbosely (without flags).

        Parameters
        ----------
        tarball : str
                Full path location of an archive on HPSS to extract from.

        fileset : list
                List containing filenames, patterns, or directories to extract from
                the archive.  If empty, then all files will be extracted.
        """
        output = self.extract(tarball, fileset, flags="-v")

        return output

    def tell(self, tarball: str, flags: str = "", fileset: list = []) -> str:
        """ Method to list the contents of an archive on HPSS

        Parameters
        ----------
        flags : str
                String of flags to send to htar.

        tarball : str
                Full path location on HPSS to list the contents of.

        fileset : list
                List containing filenames, patterns, or directories to list.
                If empty, then all files will be listed.
        """
        args = ["-t"]

        # Parse any htar flags
        if len(flags) > 0:
            args += [flags.split(" ")]

        args += ["-f", tarball]

        if len(fileset) > 0:
            args += " ".join(fileset)

        output = self.htar(args)

        return output
