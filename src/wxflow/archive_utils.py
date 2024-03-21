from logging import getLogger
from .executable import Executable, which

from .fsutils import cp, mkdir, is_rstprod

__all__ = ['Hsi']

logger = getLogger(__name__.split('.')[-1])

class Hsi:
    """Class providing a set of functions to interact with the hsi utility.

    """

    @staticmethod
    def hsi(*args) -> None:
        """Direct command builder function for hsi based on the input arguments.

        `args` should consist of a set of string arguments to send to hsi
        For example, hsi.hsi("get","some_local_file : /some/hpss/file") will execute
        hsi get some_local_file : /some/hpss/file

        """

        cmd = which("hsi", required = True)

        for arg in args:
            cmd.add_default_arg(arg)

        cmd()


    @classmethod
    def get(cls, source: str, target: str = "", hsi_flags: str = "") -> None:
        """ Function to get a file from HPSS via hsi

        Parameters
        ----------
        source : str
                Full path location on HPSS of the file

        target : str
                Location on the local machine to place the file.  If not specified,
                then the file will be placed in the current directory.

        hsi_flags : str
                String of flags to send to hsi.  See _parse_hsi_flags below for a
                full list.
        """
        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args = args + cls._parse_hsi_flags(hsi_flags)

        args = ("get",)
        if len(target) == 0:
            args = args + (source,)
        else:
            args = args + (target + " : " + source,)
        cls.hsi(*args)


    @classmethod
    def put(cls, source: str, target: str, hsi_flags: str = "", listing_file : str = None) -> None:
        """ Function to put a file onto HPSS via hsi

        Parameters
        ----------
        source : str
                Location on the local machine of the source file to send to HPSS.

        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi.  See _parse_hsi_flags below for a
                full list.
        """
        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args = args + cls._parse_hsi_flags(hsi_flags)

        args = args + ("put",)
        args = args + (source + " : " + target,)
        cls.hsi(*args)


    @classmethod
    def chmod(cls, mod: str, target: str, hsi_flags: str = "", flags: str = "") -> None:
        """ Function to change the permissions of a file or directory on HPSS

        Parameters
        ----------
        mod : str
                Permissions to set for the file or directory, e.g. "640", "o+r", etc.

        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi.  See _parse_hsi_flags below for a
                full list.

        flags : str
                Flags to send to chmod.  Valid flags are -d, -f, -h, -H, and -R.  See
                "hsi chmod -?" for more details.
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args = args + cls._parse_hsi_flags(hsi_flags)

        args = args + ("chmod",)

        if len(flags) > 0:
            valid_flags = ["d", "h", "H", "R", "f"]
            args = args + cls._parse_flags(flags, valid_flags)

        args = args + (mod,)
        args = args + (target,)
        cls.hsi(*args)


    @classmethod
    def chgrp(cls, group_name: str, target: str, hsi_flags: str = "", flags: str = "") -> None:
        """ Function to change the group of a file or directory on HPSS

        Parameters
        ----------
        group_name : str
                The group to which ownership of the file/directory is to be set.

        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi.  See _parse_hsi_flags below for a
                full list.

        flags : str
                Flags to send to chmod.  Valid flags are -h, -L, -H, and -R.  See
                "chgrp --help" for more details.
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args = args + cls._parse_hsi_flags(hsi_flags)

        args = args + ("chgrp",)

        if len(flags) > 0:
            valid_flags = ["R", "h", "L", "H"]
            args = args + cls._parse_flags(flags, valid_flags)

        args = args + (group_name,)
        args = args + (target,)
        cls.hsi(*args)


    @classmethod
    def rm(cls, target: str, hsi_flags: str = "", flags: str = "") -> None:
        """ Function to delete a file or directory on HPSS via hsi

        Parameters
        ----------
        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi.  See _parse_hsi_flags below for a
                full list.

        flags : str
                Flags to send to chmod.  The only valid flag is -R (recursive).
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args = args + cls._parse_hsi_flags(hsi_flags)

        args = args + ("rm",)

        if len(flags) > 0:
            valid_flags = ['R']
            args = args + cls._parse_flags(flags, valid_flags)

        args = args + (target,)
        cls.hsi(*args)


    @staticmethod
    def _parse_flags(flags: str, valid_flags: list, valid_flags_with_arg: list = []) -> tuple:
        """Expands the input flags into a tuple

        Inputs:
            flags: str
                String of flags to send to an hsi subcommand
            valid_flags: list of strings
                Set of valid flags to check against
            valid_flags_with_arg: list of strings
                Set of valid flags that accept arguments

        Return:
            Tuple of input flags

        Error:
            Returns ValueError if an invalid flag is in flags
        """

        expanded_flags = ()
        flags_and_args = flags.split(" ")
        n_args = len(flags_and_args)
        i = 0
        while i < n_args:
            flag = flags_and_args[i]
            # Check that the flag is valid
            if flag.startswith("-"):
                # E.g. "-p" or "-O output_file"
                if len(flag) == 2:
                    flag = flag[1]
                    if flag in valid_flags_with_arg:
                        arg = flags_and_args[i+1]
                        i += 2
                        expanded_flags = expanded_flags + ("-" + flag + arg,)
                    else:
                        expanded_flags = expanded_flags + ("-" + flag,)
                        i += 1
                # E.g. "-Ooutput_file"
                else:
                    tmp_flag = flag[1]
                    arg = flag[2:]
                    flag = tmp_flag
                    i += 1
                    expanded_flags = expanded_flags + ("-" + flag + arg,)

            else:
                raise ValueError(f"One or more input flags '{flags}' is missing a '-', unable to parse")

            if flag not in valid_flags + valid_flags_with_arg:
                raise ValueError(f"The input flags '{flags}' contains an invalid flag '{flag}'.")

        return expanded_flags


    @classmethod
    def _parse_hsi_flags(cls, flags: str) -> tuple:
        """Expands the input flags into a tuple

        Inputs:
            flags: str
                String of flags to send to hsi.  Valid flags are -a, -A, -c,
                -d, -e, -h, -k, -l, -O, -q, -s, and -v.  See hsi -q for details.

        Return:
            Tuple of input flags

        Error:
            Returns ValueError if an invalid flag is in flags
        """

        valid_flags = ["e", "p", "q", "v"]
        valid_flags_with_arg = ["a", "A", "c", "d", "h", "k", "l", "O", "s"]

        return cls._parse_flags(flags, valid_flags, valid_flags_with_arg)
