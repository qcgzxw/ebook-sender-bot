from peewee import MySQLDatabase, SqliteDatabase, PostgresqlDatabase
from playhouse.shortcuts import ReconnectMixin

from config import CONFIG


def default_config(key: str):
    return CONFIG['default'][key]


def smtp_config(key: str):
    return CONFIG['smtp'][key]


def telegram_config(key: str):
    return CONFIG['telegram'][key]


def is_windows():
    return CONFIG['default']['platform'] == 'Windows'


def database_config():
    if default_config('database') == 'mysql':
        return ReconnectMySQLDatabase(
            database=CONFIG['mysql']['name'],
            host=CONFIG['mysql']['host'],
            port=int(CONFIG['mysql']['port']),
            user=CONFIG['mysql']['user'],
            password=CONFIG['mysql']['password']
        )
    elif default_config('database') == 'sqlite':
        return SqliteDatabase(
            CONFIG['sqlite']['name'],
            pragmas={
                'journal_mode': 'wal',
                'cache_size': -1 * 64000,
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0
            }
        )
    elif default_config('database') == 'postgresql':
        return PostgresqlDatabase(
            dbname=CONFIG['mysql']['name'],
            host=CONFIG['mysql']['host'],
            port=int(CONFIG['mysql']['port']),
            user=CONFIG['mysql']['user'],
            password=CONFIG['mysql']['password']
        )
    else:
        return SqliteDatabase(
            'database.db',
            pragmas={
                'journal_mode': 'wal',
                'cache_size': -1 * 64000,
                'foreign_keys': 1,
                'ignore_check_constraints': 0,
                'synchronous': 0
            }
        )


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase):
    pass
