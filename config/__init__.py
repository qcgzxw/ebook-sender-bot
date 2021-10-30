import configparser

import platform

CONFIG = configparser.RawConfigParser(allow_no_value=True)
CONFIG.read('config.ini')
CONFIG.set('default', 'platform', platform.system())
