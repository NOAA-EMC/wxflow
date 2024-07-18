import os
from pathlib import Path

import pytest

from wxflow import CommandNotFoundError, Executable, ProcessError, which

script = """#!/bin/bash
echo ${USER}
"""

script_with_args = """#!/bin/bash

# Initialize variables
opt_o_args=()
opt_c_args=()
opt_e_args=()

# Function to display usage
usage() {
  echo "Usage: $0 [-o <arg1> <arg2> ...] [-c <arg1> <arg2> ...] [-e <arg1> <arg2> ...]"
  exit 1
}

# Parse options
while [[ $# -gt 0 ]]; do
  case $1 in
    -o)
      shift
      while [[ $# -gt 0 && $1 != -* ]]; do
        opt_o_args+=("$1")
        shift
      done
      ;;
    -c)
      shift
      while [[ $# -gt 0 && $1 != -* ]]; do
        opt_c_args+=("$1")
        shift
      done
      ;;
    -e)
      shift
      while [[ $# -gt 0 && $1 != -* ]]; do
        opt_e_args+=("$1")
        shift
      done
      ;;
    -*)
      echo "Invalid option: $1" >&2
      usage
      ;;
    *)
      echo "Invalid argument: $1" >&2
      usage
      ;;
  esac
done

user_call="${BASH_SOURCE[0]}"
# Print the optional arguments for each option
if [ ${#opt_o_args[@]} -gt 0 ]; then
  user_call="${user_call} -o"
  for arg in "${opt_o_args[@]}"; do
    user_call="${user_call} $arg"
  done
fi

if [ ${#opt_c_args[@]} -gt 0 ]; then
  user_call="${user_call} -c"
  for arg in "${opt_c_args[@]}"; do
    user_call="${user_call} $arg"
  done
fi

if [ ${#opt_e_args[@]} -gt 0 ]; then
  user_call="${user_call} -e"
  for arg in "${opt_e_args[@]}"; do
    user_call="${user_call} $arg"
  done
fi

echo "${user_call}"
"""


def test_executable(tmp_path):
    """
    Tests the class `Executable`
    Parameters:
    -----------
    tmp_path : Path
        temporary path created by pytest
    """
    whoami = os.environ['USER']

    test_file = tmp_path / 'whoami.x'
    Path(test_file).touch(mode=0o755)
    with open(test_file, 'w') as fh:
        fh.write(script)

    cmd = Executable(str(test_file))
    assert cmd.exe == [str(test_file)]

    stdout_file = tmp_path / 'stdout'
    stderr_file = tmp_path / 'stderr'
    cmd(output=str(stdout_file), error=str(stderr_file))
    with open(str(stdout_file)) as fh:
        assert fh.read() == whoami + '\n'


def test_which(tmpdir):
    """
    Tests the `which()` function.
    `which` should return `None` if the executable is not found
    Parameters
    ----------
    tmpdir : Path
        path to a temporary directory created by pytest
    """
    os.environ["PATH"] = str(tmpdir)
    assert which('test.x') is None

    with pytest.raises(CommandNotFoundError):
        which('test.x', required=True)

    path = str(tmpdir.join("test.x"))

    # create a test.x executable in the tmpdir
    with tmpdir.as_cwd():
        Path('test.x').touch(mode=0o755)

        exe = which("test.x")
        assert exe is not None
        assert exe.path == path


def test_stderr(tmp_path):
    """
    Tests the `stderr` attribute of the `Executable` class
    """

    os.environ["PATH"] = "/usr/bin:/bin"

    cmd = which("ls", required=True)

    stdout_file = tmp_path / 'stdout'
    stderr_file = tmp_path / 'stderr'
    cmd("--myopt", output=str(stdout_file), error=str(stderr_file), fail_on_error=False)

    # Assert there is no stdout
    with open(str(stdout_file)) as fh:
        assert fh.read() == ''

    # Assert stderr is not empty, '--help' is an unrecognized option
    with open(str(stderr_file)) as fh:
        stderr = fh.read()
        assert stderr != ''
        print(stderr)
        # Depending on the OS, the error message may vary
        # This was seen on macOS
        # assert stderr == "ls: unrecognized option `--myopt'" + '\n' + \
        # "usage: ls [-@ABCFGHILOPRSTUWabcdefghiklmnopqrstuvwxy1%,] [--color=when] [-D format] [file ...]" + '\n'


def test_executable_arg(tmp_path):
    test_file = tmp_path / 'exec_args.x'
    Path(test_file).touch(mode=0o755)
    with open(test_file, 'w') as fh:
        fh.write(script_with_args)

    cmd = Executable(str(test_file))
    args_list = ['-c', 'a.cfg', 'b.cfg', '-e', 'e.env']
    cmd(*args_list)

    stdout_file = tmp_path / 'stdout.arg'
    stderr_file = tmp_path / 'stderr.arg'
    cmd(*args_list, output=str(stdout_file), error=str(stderr_file))
    truth = f"{str(test_file)} {' '.join(args_list)}"
    with open(str(stdout_file)) as fh:
        assert fh.read() == truth + '\n'
