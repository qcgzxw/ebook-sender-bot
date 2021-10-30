from config import CONFIG


def default_config(key: str):
    return CONFIG['default'][key]


def smtp_config(key: str):
    return CONFIG['smtp'][key]


def telegram_config(key: str):
    return CONFIG['telegram'][key]


def is_windows():
    return CONFIG['default']['platform'] == 'Windows'
