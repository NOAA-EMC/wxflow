from .executable import which

__all__ = ['Hsi']


class Hsi:
    """
    Class offering an interface to HPSS via the hsi utility.

    Examples:
    --------

    >>> from wxflow import Hsi
    >>> hsi = Hsi()  # Generates an Executable object of "hsi"
    >>> output = hsi.put("some_local_file", "/HPSS/path/to/some_file") # Put a file onto HPSS
    >>> output = hsi.ls("/HPSS/path/to/some_file") # List the file
    >>> output = hsi.chgrp("rstprod", "/HPSS/pth/to/some_file") # Change the group to rstprod
    """

    def __init__(self):
        """Instantiate the hsi command
        """

        self.exe = which("hsi", required=True)

    def hsi(self, args: list, silent: bool = False, ignore_errors: list = []) -> str:
        """Direct command builder function for hsi based on the input arguments.

        args: list
            A list of arguments to sent to hsi

        silent: bool
            Whether the output of the hsi command should be written to stdout

        ignore_errors: list
            List of error numbers to ignore.  For example, hsi returns error
            number 64 if a target file does not exist on HPSS.

        Return: str
            Concatenated output and error of the hsi command.

        Example:
        --------
            >>> hsi = Hsi()
            >>> # Execute `hsi get some_local_file : /some/hpss/file`
            >>> hsi.hsi(["get","some_local_file : /some/hpss/file"])
        """

        if silent:
            output = self.exe(*args, output=str, error=str,
                              ignore_errors=ignore_errors)
        else:
            output = self.exe(*args, output=str.split, error=str.split,
                              ignore_errors=ignore_errors)

        return output

    def get(self, source: str, target: str = "", hsi_flags: str = "-q -e") -> str:
        """ Function to get a file from HPSS via hsi

        Parameters
        ----------
        source : str
                Full path location on HPSS of the file

        target : str
                Location on the local machine to place the file.  If not specified,
                then the file will be placed in the current directory.

        hsi_flags : str
                String of flags to send to hsi. By default, suppress login info and
                echo the get command.
        """
        args = []

        # Convert to str to handle Path objects
        target = str(target)
        source = str(source)

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args.extend(hsi_flags.split(" "))

        args.append("get")
        if len(target) == 0:
            args.append(source)
        else:
            args.append(target + " : " + source)

        output = self.hsi(args)

        return output

    def put(self, source: str, target: str, hsi_flags: str = "-q -e",
            listing_file: str = None) -> str:
        """ Function to put a file onto HPSS via hsi

        Parameters
        ----------
        source : str
                Location on the local machine of the source file to send to HPSS.

        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi. By default, suppress login info
                and echo the put command.
        """
        args = []

        # Convert to str to handle Path objects
        target = str(target)
        source = str(source)

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args.extend(hsi_flags.split(" "))

        args.append("put")
        args.append(source + " : " + target)
        output = self.hsi(args)

        return output

    def chmod(self, mod: str, target: str, hsi_flags: str = "-q -e",
              chmod_flags: str = "") -> str:
        """ Function to change the permissions of a file or directory on HPSS

        Parameters
        ----------
        mod : str
                Permissions to set for the file or directory,
                e.g. "640", "o+r", etc.

        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi. By default, suppress login info.

        chmod_flags : str
                Flags to send to chmod. See "hsi chmod -?" for more details.
        """

        args = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args.extend(hsi_flags.split(" "))

        args.append("chmod")

        if len(chmod_flags) > 0:
            args.extend(chmod_flags.split(" "))

        args.append(mod)
        args.append(target)
        output = self.hsi(args)

        return output

    def chgrp(self, group_name: str, target: str, hsi_flags: str = "-q",
              chgrp_flags: str = "") -> str:
        """ Function to change the group of a file or directory on HPSS

        Parameters
        ----------
        group_name : str
                The group to which ownership of the file/directory is to be set.

        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi. By default, suppress login info.

        chgrp_flags : str
                Flags to send to chgrp.  See "hsi chgrp -?" for more details.
        """

        args = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args.extend(hsi_flags.split(" "))

        args.append("chgrp")

        if len(chgrp_flags) > 0:
            args.extend(chgrp_flags.split(" "))

        args.append(group_name)
        args.append(target)
        output = self.hsi(args)

        return output

    def rm(self, target: str, hsi_flags: str = "-q -e", rm_flags: str = "") -> str:
        """ Function to delete a file or directory on HPSS via hsi

        Parameters
        ----------
        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi. By default, suppress login info
                and echo the rm command.

        rm_flags : str
                Flags to send to rm.  See "hsi rm -?" for more details.
        """

        # Call rmdir if recursive (-r) flag present
        if "-r" in rm_flags:
            rmdir_flags = rm_flags.replace("-r", "")
            output = self.rmdir(target, hsi_flags, rmdir_flags)
            return output

        args = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args.extend(hsi_flags.split(" "))

        args.append("rm")

        if len(rm_flags) > 0:
            args.extend(rm_flags.split(" "))

        args.append(target)
        output = self.hsi(args)

        return output

    def rmdir(self, target: str, hsi_flags: str = "-q -e", rmdir_flags: str = "") -> str:
        """ Function to delete a file or directory on HPSS via hsi

        Parameters
        ----------
        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi. By default, suppress login info
                and echo the rmdir command.

        rmdir_flags : str
                Flags to send to rmdir.  See "hsi rmdir -?" for more details.
        """

        args = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args.extend(hsi_flags.split(" "))

        args.append("rmdir")

        if len(rmdir_flags) > 0:
            args.extend(rmdir_flags.split(" "))

        args.append(target)
        output = self.hsi(args)

        return output

    def mkdir(self, target: str, hsi_flags: str = "-q -e", mkdir_flags: str = "") -> str:
        """ Function to delete a file or directory on HPSS via hsi

        Parameters
        ----------
        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi. By default, suppress login info
                and echo the mkdir command.
        """

        args = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args.extend(hsi_flags.split(" "))

        # The only flag available for mkdir is -p, which we will use.
        args.extend(["mkdir", "-p"])

        if len(mkdir_flags) > 0:
            args.extend(mkdir_flags.split(" "))

        args.append(target)
        output = self.hsi(args)

        return output

    def ls(self, target: str, hsi_flags: str = "-q", ls_flags: str = "",
           ignore_missing: bool = False) -> str:
        """ Function to list files/directories on HPSS via hsi

        Parameters
        ----------
        target : str
            Full path of the target location on HPSS.

        hsi_flags : str
            String of flags to send to hsi. By default, suppress login info.

        ls_flags : str
            Flags to send to ls.  See "hsi ls -?" for more details.

        ignore_missing: bool
            Flag to ignore missing files
        """

        args = []

        if ignore_missing:
            ignore_errors = [64]
        else:
            ignore_errors = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args.extend(hsi_flags.split(" "))

        args.append("ls")

        # Parse any ls flags
        if len(ls_flags) > 0:
            args.extend(ls_flags.split(" "))

        args.append(target)
        output = self.hsi(args, ignore_errors=ignore_errors)

        return output

    def exists(self, target: str) -> bool:
        """ Function to test the existence of a file/directory/glob on HPSS

        Parameters
        ----------
        target : str
                Full path of the target location on HPSS.

        Return: bool
                True if the target exists on HPSS.
        """

        args = ["-q", "ls", target]

        # Do not exit if the file is not found; do not pipe output to stdout
        output = self.hsi(args, silent=True, ignore_errors=[64])

        if "HPSS_ENOENT" in output:
            return False
        # Catch wildcards
        elif f"Warning: No matching names located for '{target}'" in output:
            return False
        else:
            return True
