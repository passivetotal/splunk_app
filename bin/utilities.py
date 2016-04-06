import ConfigParser
import logging
import logging.handlers
import os
import splunk
import StringIO
import subprocess

DEFAULT_SPLUNK = '/Applications/Splunk'


def QuotaException(Exception):
    """Generic quota exception to control errors."""
    pass


def setup_logging():
    """Build a logger for debugging purposes."""
    logger = logging.getLogger('splunk.passivetotal')
    SPLUNK_HOME = os.environ['SPLUNK_HOME']
    LOGGING_DEFAULT_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log.cfg')
    LOGGING_LOCAL_CONFIG_FILE = os.path.join(SPLUNK_HOME, 'etc', 'log-local.cfg')
    LOGGING_STANZA_NAME = 'python'
    LOGGING_FILE_NAME = "passivetotal.log"
    BASE_LOG_PATH = os.path.join('var', 'log', 'splunk')
    LOGGING_FORMAT = "%(asctime)s %(levelname)-s\t%(module)s:%(lineno)d - %(message)s"
    splunk_log_handler = logging.handlers.RotatingFileHandler(
        os.path.join(SPLUNK_HOME, BASE_LOG_PATH, LOGGING_FILE_NAME), mode='a')
    splunk_log_handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
    logger.addHandler(splunk_log_handler)
    splunk.setupSplunkLogger(logger, LOGGING_DEFAULT_CONFIG_FILE,
                             LOGGING_LOCAL_CONFIG_FILE, LOGGING_STANZA_NAME)
    return logger


def get_config(conf_file_name, section):
    """Read in the Splunk configuration to extract the username and API key.
    :param conf_file_name: Name of the configuration file
    :param section: Section to read from the configuration
    :return: Dict of parsed configuration section
    """
    env = dict()
    env.update(os.environ)
    splunk_home = env.get('SPLUNK_HOME', DEFAULT_SPLUNK)
    btool = os.path.join(splunk_home, "bin", "btool")
    tmp = subprocess.Popen([btool, conf_file_name, "list"],
                           stdout=subprocess.PIPE, env=env)
    (output, error) = tmp.communicate()

    f = StringIO.StringIO()
    f.write(output)
    f.seek(0)
    cfgparse = ConfigParser.RawConfigParser()
    cfgparse.readfp(f)

    cfg = dict()
    for opt in cfgparse.options(section):
        cfg[opt] = cfgparse.get(section, opt)
    return cfg


def gen_label(item):
    """Generate a friendly looking label based on a string.
    :param item: Str value to clean up
    :return: Cleaned up label based on a key
    """
    output = list()
    for idx, chr in enumerate(item):
        if chr.isupper():
            output.append(' ')
        if idx == 0:
            chr = chr.upper()
        output.append(chr)
    return ''.join(output)


def build_headers():
    """Build a set of headers to use when making requests."""
    headers = dict()
    headers['PT-Integration'] = 'Splunk v1.0.0'
    return headers
