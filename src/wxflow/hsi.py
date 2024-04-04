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

    def __init__(self, def_hsi_args: list = ["-q", "-e"]):
        """Instantiate the hsi command

        def_hsi_args: str
            List of default arguments to send to hsi.  The defaults are
            -q: run in quiet mode (do not print login information)
            -e: echo each command
        """

        self.exe = which("hsi", required=True)

        for arg in def_hsi_args:
            self.exe.add_default_arg(arg)

    def _hsi(self, arg_list: list, silent: bool = False, ignore_errors: list = []) -> str:
        """Direct command builder function for hsi based on the input arguments.

        arg_list: list
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
            output = self.exe(*arg_list, output=str, error=str,
                              ignore_errors=ignore_errors)
        else:
            output = self.exe(*arg_list, output=str.split, error=str.split,
                              ignore_errors=ignore_errors)

        return output

    def get(self, source: str, target: str = "", hsi_flags: str = "") -> str:
        """ Method to get a file from HPSS via hsi

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
        arg_list = []

        # Convert to str to handle Path objects
        target = str(target)
        source = str(source)

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            arg_list.extend(hsi_flags.split(" "))

        arg_list.append("get")
        if len(target) == 0:
            arg_list.append(source)
        else:
            arg_list.append(target + " : " + source)

        output = self._hsi(arg_list)

        return output

    def put(self, source: str, target: str, hsi_flags: str = "",
            listing_file: str = None) -> str:
        """ Method to put a file onto HPSS via hsi

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
        arg_list = []

        # Convert to str to handle Path objects
        target = str(target)
        source = str(source)

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            arg_list.extend(hsi_flags.split(" "))

        arg_list.append("put")
        arg_list.append(source + " : " + target)
        output = self._hsi(arg_list)

        return output

    def chmod(self, mod: str, target: str, hsi_flags: str = "",
              chmod_flags: str = "") -> str:
        """ Method to change the permissions of a file or directory on HPSS

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

        arg_list = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            arg_list.extend(hsi_flags.split(" "))

        arg_list.append("chmod")

        if len(chmod_flags) > 0:
            arg_list.extend(chmod_flags.split(" "))

        arg_list.append(mod)
        arg_list.append(target)
        output = self._hsi(arg_list)

        return output

    def chgrp(self, group_name: str, target: str, hsi_flags: str = "",
              chgrp_flags: str = "") -> str:
        """ Method to change the group of a file or directory on HPSS

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

        arg_list = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            arg_list.extend(hsi_flags.split(" "))

        arg_list.append("chgrp")

        if len(chgrp_flags) > 0:
            arg_list.extend(chgrp_flags.split(" "))

        arg_list.append(group_name)
        arg_list.append(target)
        output = self._hsi(arg_list)

        return output

    def rm(self, target: str, hsi_flags: str = "", rm_flags: str = "") -> str:
        """ Method to delete a file or directory on HPSS via hsi

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

        arg_list = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            arg_list.extend(hsi_flags.split(" "))

        arg_list.append("rm")

        if len(rm_flags) > 0:
            arg_list.extend(rm_flags.split(" "))

        arg_list.append(target)

        # Ignore missing files
        output = self._hsi(arg_list, ignore_errors=[72])

        return output

    def rmdir(self, target: str, hsi_flags: str = "", rmdir_flags: str = "") -> str:
        """ Method to delete a directory on HPSS via hsi

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

        arg_list = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            arg_list.extend(hsi_flags.split(" "))

        arg_list.append("rmdir")

        if len(rmdir_flags) > 0:
            arg_list.extend(rmdir_flags.split(" "))

        arg_list.append(target)
        output = self._hsi(arg_list)

        return output

    def mkdir(self, target: str, hsi_flags: str = "", mkdir_flags: str = "") -> str:
        """ Method to delete a file or directory on HPSS via hsi

        Parameters
        ----------
        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi. By default, suppress login info
                and echo the mkdir command.
        """

        arg_list = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            arg_list.extend(hsi_flags.split(" "))

        # The only flag available for mkdir is -p, which we will use.
        arg_list.extend(["mkdir", "-p"])

        if len(mkdir_flags) > 0:
            arg_list.extend(mkdir_flags.split(" "))

        arg_list.append(target)
        output = self._hsi(arg_list)

        return output

    def ls(self, target: str, hsi_flags: str = "", ls_flags: str = "",
           ignore_missing: bool = False) -> str:
        """ Method to list files/directories on HPSS via hsi

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

        arg_list = []

        if ignore_missing:
            ignore_errors = [64]
        else:
            ignore_errors = []

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            arg_list.extend(hsi_flags.split(" "))

        arg_list.append("ls")

        # Parse any ls flags
        if len(ls_flags) > 0:
            arg_list.extend(ls_flags.split(" "))

        arg_list.append(target)
        output = self._hsi(arg_list, ignore_errors=ignore_errors)

        return output

    def exists(self, target: str) -> bool:
        """ Method to test the existence of a file/directory/glob on HPSS

        Parameters
        ----------
        target : str
                Full path of the target location on HPSS.

        Return: bool
                True if the target exists on HPSS.
        """

        arg_list = ["-q", "ls", target]

        # Do not exit if the file is not found; do not pipe output to stdout
        output = self._hsi(arg_list, silent=True, ignore_errors=[64])

        if "HPSS_ENOENT" in output:
            return False
        # Catch wildcards
        elif f"Warning: No matching names located for '{target}'" in output:
            return False
        else:
            return True
