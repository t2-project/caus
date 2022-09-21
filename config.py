import configparser
import os

_config : configparser.ConfigParser = None

def get_config() -> configparser.ConfigParser:
    """
    Returns the config for this CAUS.
    The result of this method will be cached and reused for subsequent calls.
    Default file is ./config.ini
    Can be customised by setting the environment variable CAUS_CONFIG
    """
    global _config
    if _config is None:
        _config = configparser.ConfigParser()
        _config.read(os.environ.get('CAUS_CONFIG', 'config.ini'))
    return _config