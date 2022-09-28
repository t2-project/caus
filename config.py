import configparser
import os
from typing import Optional

_config: Optional[configparser.ConfigParser] = None


def get_config() -> configparser.ConfigParser:
    """Returns the config for this CAUS.

    The result of this method will be cached and reused for subsequent calls.
    Default file is ./config.ini
    Can be customised by setting the environment variable CAUS_CONFIG

    Returns:
        the configparser containing the configuration for the whole CAUS
    """
    global _config
    if _config is None:
        _config = configparser.ConfigParser()
        _config.read(os.environ.get("CAUS_CONFIG", "config.ini"))
    return _config
