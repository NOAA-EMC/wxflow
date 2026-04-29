import io
import logging
import re
import sys

import pytest

from wxflow import Logger, add_file_logger, add_stream_logger, logit

# Regex that matches ANSI escape sequences (e.g. \x1b[38;21m)
ANSI_ESCAPE_RE = re.compile(r'\x1b\[[0-9;]*m')

level = 'debug'
reference = {'debug': "Logging test has started",
             'info': "Logging to 'logger.log' in the script dir",
             'warning': "This is my last warning, take heed",
             'error': "This is an error",
             'critical': "He's dead, She's dead.  They are all dead!"}
number_of_log_msgs = len(reference.keys())


@pytest.fixture(scope='module')
def logger_init():
    """Test logger initialization"""

    try:
        _ = Logger(level='info', stdout=False, colored_log=False)
    except Exception as ee:
        raise AssertionError(f'Logger initialization failed as {ee}')

    assert True, "Logger initialized successfully"


def test_logger_stdout(logger_init):
    """Test log to stdout"""

    try:
        log = logging.getLogger('test_logger_stdout')
        add_stream_logger(log, level='warning', colored_log=True)
        log.debug(reference['debug'])
        log.info(reference['info'])
        log.warning(reference['warning'])
        log.error(reference['error'])
        log.critical(reference['critical'])
    except Exception as e:
        raise AssertionError(f'Logging to stdout failed as {e}')

    assert True, "Logger to stdout tested successfully"


def test_logger_file(tmp_path, logger_init):
    """Test log to file"""

    logfile = tmp_path / "logger.log"

    try:
        log = logging.getLogger('test_logger_file')
        add_file_logger(log, level='debug', logfile_path=logfile)
        # Since the lowest logger level in root is 'info', we need to reduce the level to 'debug' to all loggers
        log.setLevel(logging.DEBUG)
        log.debug(reference['debug'])
        log.info(reference['info'])
        log.warning(reference['warning'])
        log.error(reference['error'])
        log.critical(reference['critical'])
    except Exception as e:
        raise AssertionError(f'logging failed as {e}')

    # Make sure log to file created messages
    try:
        with open(logfile, 'r') as fh:
            log_msgs = fh.readlines()
    except Exception as e:
        raise AssertionError(f'failed reading log file as {e}')

    # Ensure number of messages are same
    log_msgs_in_logfile = len(log_msgs)
    assert log_msgs_in_logfile == number_of_log_msgs, \
        f"Expected {number_of_log_msgs} messages, but found {log_msgs_in_logfile}"

    # Ensure messages themselves are same
    for line in log_msgs:
        lev = line.split('-')[3].strip().lower()
        message = line.split(':')[-1].strip()
        assert reference[lev] == message, \
            f"Expected message '{reference[lev]}' but found '{message}' in log file"


def test_logger_logit_stdout(logger_init):

    logger = Logger('test_logit', level=level, colored_log=True)

    @logit(logger)
    def add(x, y):
        return x + y

    @logit(logger)
    def usedict(n, j=0, k=1):
        return n + j + k

    @logit(logger, 'example')
    def spam():
        print('Spam!')

    add(2, 3)
    usedict(2, 3)
    usedict(2, k=3)
    spam()

    assert True


def test_logger_logit_logfile(tmp_path, logger_init):

    logfile = tmp_path / "logit.log"
    logger = Logger('test_logit', level=level, colored_log=True, logfile_path=logfile)

    @logit(logger)
    def add(x, y):
        return x + y

    @logit(logger)
    def usedict(n, j=0, k=1):
        return n + j + k

    @logit(logger, 'example')
    def spam():
        print('Spam!')

    add(2, 3)
    usedict(2, 3)
    usedict(2, k=3)
    spam()

    # Verify that file paths are logged
    with open(logfile, 'r') as fh:
        log_contents = fh.read()

    # Assert that the message contains the test file name full path
    assert 'BEGIN: tests.test_logger.add: ' + str(__file__) in log_contents, \
        "Expected test file name to be logged"

    # Assert that no ANSI escape codes are present in the log file even though
    # colored_log=True was requested (file is not a TTY)
    assert not ANSI_ESCAPE_RE.search(log_contents), \
        "Log file must not contain ANSI escape/formatting characters"


def test_logger_logit_instance_method(tmp_path, logger_init):

    logfile = tmp_path / "logit_instance.log"
    logger = Logger('test_logit_instance', level=level, colored_log=True, logfile_path=logfile)

    class MyClass:
        @logit(logger)
        def instance_method(self, x):
            return x * 2

    obj = MyClass()
    result = obj.instance_method(5)
    assert result == 10, "Expected instance method to return 10"

    # Verify that file paths are logged
    with open(logfile, 'r') as fh:
        log_contents = fh.read()

    # Assert that the message contains the test file name full path
    assert 'BEGIN: tests.test_logger.instance_method: ' + str(__file__) in log_contents
    assert 'MyClass object' in log_contents, "Expected MyClass method name to be logged. Actual log contents: " + log_contents


def test_logger_logit_noninstance_method(tmp_path, logger_init):

    logfile = tmp_path / "logit_noninstance.log"
    logger = Logger('test_logit_noninstance', level=level, colored_log=True, logfile_path=logfile)

    class DummyClass:
        def __str__(self):
            return "DummyClass instance"

    class MyClass:
        @staticmethod
        @logit(logger)
        def non_instance_method(x):
            return x * 3

        @staticmethod
        @logit(logger)
        def non_instance_method_object_arg(obj):
            return str(obj)

    result = MyClass.non_instance_method(5)
    assert result == 15, "Expected non-instance method to return 15"

    obj = DummyClass()

    result = MyClass.non_instance_method_object_arg(obj)
    assert result == "DummyClass instance", "Expected non-instance method to return string representation of DummyClass instance"

    # Check the logfile for correct logging of non-instance method and object argument
    with open(logfile, 'r') as fh:
        log_contents = fh.read()
    assert 'BEGIN: tests.test_logger.non_instance_method: ' + str(__file__) in log_contents, \
        "Expected non-instance method name to be logged. Actual log contents: " + log_contents

    assert 'BEGIN: tests.test_logger.non_instance_method_object_arg: ' + str(__file__) in log_contents, \
        "Expected non-instance method name to be logged. Actual log contents: " + log_contents

    # Make sure that the string representation is not simply'DummyClass object' but includes the instance's memory address (default __str__ for objects)
    assert 'DummyClass object at' in log_contents, \
        "Expected string representation of DummyClass instance to be logged. Actual log contents: " + log_contents


def test_stream_logger_no_ansi_on_non_tty(logger_init):
    """Test that colored_log=True does not emit ANSI codes when stream is not a TTY"""

    stream = io.StringIO()
    log = logging.getLogger('test_no_ansi_non_tty')
    add_stream_logger(log, level='debug', colored_log=True, stream=stream)
    log.setLevel(logging.DEBUG)
    log.debug(reference['debug'])
    log.info(reference['info'])
    log.warning(reference['warning'])
    log.error(reference['error'])
    log.critical(reference['critical'])

    content = stream.getvalue()
    assert not ANSI_ESCAPE_RE.search(content), \
        "Stream output must not contain ANSI escape/formatting characters when stream is not a TTY"


def test_stream_logger_ansi_on_tty(logger_init):
    """Test that colored_log=True emits ANSI codes when stream is a TTY"""

    class _FakeTTY(io.StringIO):
        def isatty(self):
            return True

    stream = _FakeTTY()
    log = logging.getLogger('test_ansi_tty')
    add_stream_logger(log, level='debug', colored_log=True, stream=stream)
    log.setLevel(logging.DEBUG)
    log.info(reference['info'])

    content = stream.getvalue()
    assert ANSI_ESCAPE_RE.search(content), \
        "Stream output must contain ANSI escape/formatting characters when stream is a TTY and colored_log=True"


def test_file_logger_no_ansi(tmp_path, logger_init):
    """Test that log files written via add_file_logger never contain ANSI codes"""

    logfile = tmp_path / "no_ansi.log"
    log = logging.getLogger('test_file_no_ansi')
    add_file_logger(log, level='debug', logfile_path=logfile)
    log.setLevel(logging.DEBUG)

    for msg in reference.values():
        log.debug(msg)
        log.info(msg)
        log.warning(msg)
        log.error(msg)
        log.critical(msg)

    with open(logfile, 'r') as fh:
        log_contents = fh.read()

    assert not ANSI_ESCAPE_RE.search(log_contents), \
        "Log file written by add_file_logger must not contain ANSI escape/formatting characters"


def test_stream_logger_no_ansi_when_stdout_redirected(logger_init, monkeypatch):
    """Test that no ANSI codes appear when sys.stdout is redirected (bash: script.py > log.txt)

    Simulates what happens when an entire bash script is redirected to a file.
    add_stream_logger is called without an explicit stream so it uses sys.stdout,
    which is no longer a TTY when redirected by the shell.
    """

    buf = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buf)

    log = logging.getLogger('test_redirected_stdout')
    # Call without explicit stream — mirrors real-world usage; sys.stdout is used internally
    add_stream_logger(log, level='debug', colored_log=True)
    log.setLevel(logging.DEBUG)
    log.debug(reference['debug'])
    log.info(reference['info'])
    log.warning(reference['warning'])
    log.error(reference['error'])
    log.critical(reference['critical'])

    content = buf.getvalue()
    assert not ANSI_ESCAPE_RE.search(content), \
        "Output must not contain ANSI escape/formatting characters when sys.stdout is redirected"


def test_logger_class_no_ansi_when_stdout_redirected(logger_init, monkeypatch):
    """Test that Logger(colored_log=True) emits no ANSI codes when sys.stdout is redirected

    Simulates: ./run_script.sh > logfile.log 2>&1
    The Logger class must automatically detect the redirection and suppress color codes.
    """

    buf = io.StringIO()
    monkeypatch.setattr(sys, 'stdout', buf)

    logger = Logger('test_logger_redirect', level='debug', colored_log=True)
    logger.setLevel(logging.DEBUG)
    logger.debug(reference['debug'])
    logger.info(reference['info'])
    logger.warning(reference['warning'])
    logger.error(reference['error'])
    logger.critical(reference['critical'])

    content = buf.getvalue()
    assert not ANSI_ESCAPE_RE.search(content), \
        "Logger output must not contain ANSI escape/formatting characters when sys.stdout is redirected"
