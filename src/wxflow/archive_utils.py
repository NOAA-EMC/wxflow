from logging import getLogger
from .executable import Executable, which

from .fsutils import cp, mkdir, is_rstprod

__all__ = ['hsi']

logger = getLogger(__name__.split('.')[-1])

class hsi:
    """Class providing a set of functions to interact with the hsi utility.

    """


    def hsi(*args) -> None:
        """Direct command builder function for hsi based on the input arguments.

        `args` should consist of a set of string arguments to send to hsi
        For example, hsi.hsi("get","some_local_file : /some/hpss/file") will execute
        hsi get some_local_file : /some/hpss/file

        """

        cmd = which("hsi", required=True)
        for arg in args:
            cmd.add_default_arg(arg)

        cmd()


    def get(source: str, target: str = "", hsi_flags: str = "") -> None:
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
            args = args + _parse_hsi_flags(hsi_flags)

        args = ("get",)
        args = args + (target + " : " + source,)
        hsi(*args)


    def put(source: str, target: str, hsi_flags: str = "", listing_file : str = None) -> None:
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
            args = args + _parse_hsi_flags(hsi_flags)

        args = args + ("put",)
        args = args + (source + " : " + target,)
        hsi(*args)


    def chmod(mod: str, target: str, hsi_flags: str = "", flags: str = "") -> None:
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
                Flags to send to chmod.  Valid flags are -R, -f, -c, and -v.  See
                "chmod --help" for more details.
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args = args + _parse_hsi_flags(hsi_flags)

        args = args + ("chmod",)

        if len(flags) > 0:
            valid_flags = ["R", "f", "c", "v"]
            args = args + _parse_flags(flags, valid_flags)

        args = args + (mod,)
        args = args + (target,)
        hsi(*args)


    def chgrp(group_name: str, target: str, hsi_flags: str = "", flags: str = "") -> None:
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
                Flags to send to chmod.  Valid flags are -c, -v, -f, -h, and -R.  See
                "chgrp --help" for more details.
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args = args + _parse_hsi_flags(hsi_flags)

        args = args + ("chgrp",)

        if len(flags) > 0:
            valid_flags = ["c", "v", "f", "h", "R"]
            args = args + _parse_flags(flags, valid_flags)

        args = args + (group_name,)
        args = args + (target,)
        hsi(*args)


    def rm(target: str, hsi_flags: str = "", flags: str = "") -> None:
        """ Function to delete a file or directory on HPSS via hsi

        Parameters
        ----------
        target : str
                Full path of the target location of the file on HPSS.

        hsi_flags : str
                String of flags to send to hsi.  See _parse_hsi_flags below for a
                full list.

        flags : str
                Flags to send to chmod.  Valid flags are -v, -f, and -r.  See
                "rm --help" for more details.
        """

        args = ()

        # Parse any hsi flags
        if len(hsi_flags) > 0:
            args = args + _parse_hsi_flags(hsi_flags)

        args = args + ("rm",)

        if len(flags) > 0:
            valid_flags = ['r', 'f', 'v']
            args = args + _parse_flags(flags, valid_flags)

        args = args + (target,)
        hsi(*args)


    def _parse_flags(flags: str, valid_flags: list, valid_flags_with_args: list = []) -> tuple:
        """Expands the input flags into a tuple

        Inputs:
            flags: str
                String of flags to send to an hsi subcommand
            valid_flags: list of strings
                Set of valid flags to check against
            valid_flags_with_args: list of strings
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
            if flag.startswith("-")
                # E.g. "-p" or "-O output_file"
                if len(flag) == 2:
                    flag = flag[1]
                    if flag in valid_flags_with_arg:
                        arg = flags_and_args[i+1]
                        i += 2
                        expanded_flags = expanded_flags + (flag + arg,)
                    else:
                        expanded_flags = expanded_flags + (flag,)
                # E.g. "-Ooutput_file"
                else:
                    flag = flag[1]
                    arg = flag[2:]
                    i += 1
                    expanded_flags = expanded_flags + (flag + arg,)

            else:
                raise ValueError(f"One or more input flags '{flags}' is missing a '-', unable to parse")

            if flag not in valid_flags + valid_flags_with_arg:
                raise ValueError(f"The input flags '{flags}' contains an invalid flag '{flag}'."

        return expanded_flags


    def _parse_hsi_flags(flags: str) -> tuple:
        """Expands the input flags into a tuple

        Inputs:
            flags: str
                String of flags to send to hsi.  Valid flags (from hsi -?):
---------------------------------------------------------------------------
   hsi [-a acct_id|acct_name] [-A authmethod] [-c krb_cred_file] [-d level] [-e] [-G globus proxy path]
       [-h  host[/port]  [-k keytabfile] [-l loginname] [-O listingFile] [-o] [-P] [-p port] [-s site]
       [-q] [-v] [cmds]
  Parameters:
   -a acct_id | acct_name - specifies the HPSS account ID or account name to set
      after login completes. This will be used for all new file creations
   -A authmethod   - authentication method. Case-insensitive legal method names are:
      "combo","keytab","ident","gsi","local"
   -c krb_cred_file  - pathname to use for Kerberos credentials cache file
   -d debug_level - debug message level (0-5) default is 0
   -e             - command echo flag. Echos lines read from <IN> file(s) to the listable output file
   -h host - specifies host name or IP address of the HPSS server, and optionally,
      the port on which to connect
   -k keytabfile - specifies pathname to DCE keytab file
   -l loginname - specifies login name to use.
     For kerberos, this is usually of the form "name@realm"
   -O listingFile - specifies filename to contain all listable output, error messages,etc
        This option is intended for use by programs that run hsi as a child process
        and internally disables verbose (-v) mode, and sets quiet (-q) mode. (This can
        be overridden by specifying the -v or -q parameters after the -O parameter)
   -q - specifies "quiet" mode. Suppresses login message,file transfer progress messages, etc.
   -s site - specifies the site name to connect to at startup.  This name must match one of
     the stanza names in either the global hsirc file, or in the user's private .hsirc file
   -v - specifies "verbose" mode for listable output 
-------------------------------------------------------------------------------------

        Return:
            Tuple of input flags

        Error:
            Returns ValueError if an invalid flag is in flags
        """

        valid_flags = ["e", "p", "q", "v"]
        valid_flags_with_arg ["a", "A", "c", "d", "h", "k", "l", "O", "s"]

        return _parse_flags(flags, valid_flags, valid_flags_with_args)

class htar:
    """Class providing a set of functions to interact with the htar utility.

    """

    def create(target: str, fileset: list, flags: str = None, ignore_missing: bool = False) -> None:
        """ Build and execute the command
            htar <flags> -cf <target> <file_list.split()>

        Parameters:
        -----------
            target : str
                    Path to the tarball to be created on HPSS
            fileset: list
                    List of files to be added to <target>

        Keyword Argument:
        -----------------
            flags : str
                    Optional flags to add to the htar command
                    Each flag must be separated by a " " and start with a "-".
                    (-c and -f are assumed)
                    Invalid flags will raise a ValueError

            ignore_missing: bool
                    Flag specifying whether missing files are allowed.  Warnings
                    will be printed instead.

        # Will raise a CommandNotFoundError if htar is not in $PATH
        # Will raise a FileNotFoundError if an input file is not found
        # Will raise a ValueError if an invalid flag is sent in
        """
        cmd = which("htar", required=True)

        if flags is not None:
            valid_flags = ['-v', '-h', '-q', '-V', '-v']
            ignore_flags = ['-c', '-f']
            for flag in flags.split(" ")
                if flag in ignore_flags:
                    continue
                if flag not in valid_flags:
                    raise ValueError(f"The input flags '{flags}' contains an invalid flag '{flag}'."
                cmd.add_default_arg(flag)

        cmd.add_default_arg("-c")
        cmd.add_default_arg("-f")

        cmd.add_default_arg(target)

        has_rstprod = False

        # Check files for existence and rstprod
        for file in fileset
            if not os.path.exists(file):
                if ignore_missing:
                    print(f"WARNING input file '{file}' does not exist")
                else:
                    raise FileNotFoundError(f"The input file '{file}' was not found")

            if not has_rstprod:
                has_rstprod = is_rstprod(file)

            cmd.add_default_arg(file)

        if has_rstprod:
            cmd()
