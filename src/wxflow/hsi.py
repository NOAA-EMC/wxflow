from logging import getLogger
from .executable import Executable, which

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
                String of flags to send to hsi.
        """
        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args += tuple(hsi_flags.split(" "))

        args += ("get",)
        if len(target) == 0:
            args += (source,)
        else:
            args += (target + " : " + source,)
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
                String of flags to send to hsi.
        """
        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args += tuple(hsi_flags.split(" "))

        args += ("put",)
        args += (source + " : " + target,)
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
                String of flags to send to hsi.

        flags : str
                Flags to send to chmod.  Valid flags are -d, -f, -h, -H, and -R.  See
                "hsi chmod -?" for more details.
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args += tuple(hsi_flags.split(" "))

        args += ("chmod",)

        if len(flags) > 0:
            args += tuple(flags.split(" "))

        args += (mod,)
        args += (target,)
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
                String of flags to send to hsi.

        flags : str
                Flags to send to chmod.  Valid flags are -h, -L, -H, and -R.  See
                "chgrp --help" for more details.
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args += tuple(hsi_flags.split(" "))

        args += ("chgrp",)

        if len(flags) > 0:
            args += tuple(flags.split(" "))

        args += (group_name,)
        args += (target,)
        cls.hsi(*args)


    @classmethod
    def rm(cls, target: str, hsi_flags: str = "", flags: str = "") -> None:
        """ Function to delete a file or directory on HPSS via hsi

        Parameters
        ----------
        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi.

        flags : str
                Flags to send to chmod.  The only valid flag is -R (recursive).
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args += tuple(hsi_flags.split(" "))

        args += ("rm",)

        if len(flags) > 0:
            args += tuple(flags.split(" "))

        args += (target,)
        cls.hsi(*args)
