import logging

import pytest

from wxflow import Logger, add_file_logger, add_stream_logger, logit

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


def test_logger_logit(tmp_path, logger_init):

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
    assert 'Begin: tests.test_logger.add: '+ str(__file__) in log_contents, \
        "Expected test file name to be logged"
