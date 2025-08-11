import logging

from wxflow import Logger, logit#, setup_logging, add_file_logger

"""
Testing of the wxflow logger module

Testing of logging is tricky, because the logger is a singleton.
This means that the logging.getLogger should be called only once.
This is to avoid duplicate logs.

Here, this is achieved, by calling the test_logger_init first.
Without this, the wxflow.Logger will not be initialized, and the tests will fail.
"""

level = 'debug'
reference = {'debug': "Logging test has started",
             'info': "Logging to 'logger.log' in the script dir",
             'warning': "This is my last warning, take heed",
             'error': "This is an error",
             'critical': "He's dead, She's dead.  They are all dead!"}
number_of_log_msgs = len(reference.keys())


def test_logger_init():  # This should be the first test to run (always)
    """Test logger initialization"""

    # Initialize logger
    #_ = Logger(level=level, colored_log=True)
    #setup_logging(level=level, colored_log=True)
    log = logging.getLogger()
    print("Logger initialized with level:", log.level)

    #log = logging.getLogger('test_logger_init')
    #log.info("Logger initialized for test_logger_init")

    # Check if logger is initialized correctly
    #assert log.name == 'test_logger_init'


#def test_logger_stdout():
#    """Test log to stdout"""
#
#    log = logging.getLogger('test_logger_stdout', level=logging.DEBUG)
#
#    try:
#        log.debug(reference['debug'])
#        log.info(reference['info'])
#        log.warning(reference['warning'])
#        log.error(reference['error'])
#        log.critical(reference['critical'])
#    except Exception as e:
#        raise AssertionError(f'logging failed as {e}')


#def test_logger_file(tmp_path):
#    """Test log file"""
#
#    logfile = tmp_path / "logger.log"
#
#    log = logging.getLogger('test_logger_file')
#    add_file_logger(log, logfile, level=log.level)
#
#    try:
#        log.debug(reference['debug'])
#        log.info(reference['info'])
#        log.warning(reference['warning'])
#        log.error(reference['error'])
#        log.critical(reference['critical'])
#    except Exception as e:
#        raise AssertionError(f'logging failed as {e}')
#
#    # Make sure log to file created messages
#    try:
#        with open(logfile, 'r') as fh:
#            log_msgs = fh.readlines()
#    except Exception as e:
#        raise AssertionError(f'failed reading log file as {e}')
#
#    # Ensure number of messages are same
#    log_msgs_in_logfile = len(log_msgs)
#    assert log_msgs_in_logfile == number_of_log_msgs
#
#    # Ensure messages themselves are same
#    for _, line in enumerate(log_msgs):
#        lev = line.split('-')[3].strip().lower()
#        message = line.split(':')[-1].strip()
#        assert reference[lev] == message
#
#
#def test_logit():
#
#    logger = logging.getLogger('test_logit')
#
#    @logit(logger)
#    def add(x, y):
#        return x + y
#
#    @logit(logger)
#    def usedict(n, j=0, k=1):
#        return n + j + k
#
#    @logit(logger, 'example')
#    def spam():
#        print('Spam!')
#
#    add(2, 3)
#    usedict(2, 3)
#    usedict(2, k=3)
#    spam()
#
#    assert True
#