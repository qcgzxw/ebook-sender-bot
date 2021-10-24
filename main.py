import os
import platform

from dotenv import load_dotenv
from playhouse.db_url import connect

import models
from tg_bot import TgBot


def register_db() -> None:
    # more information: http://docs.peewee-orm.com/en/latest/peewee/database.html#connecting-using-a-database-url
    database = connect(os.environ.get('DATABASE', 'sqlite:///database.db'))
    models.database_proxy.initialize(database)
    database.create_tables([models.User, models.UserEmail, models.UserSendLog])


def run_tg_bot() -> None:
    bot_token = os.getenv('TELEGRAM_TOKEN')
    develop_chat_id = os.getenv('TELEGRAM_DEVELOP_CHAT_ID', '')
    bot = TgBot(bot_token, develop_chat_id)
    bot.run()


def main() -> None:
    load_dotenv()
    os.environ["SYSTEM_PLATFORM"] = platform.system()
    register_db()
    run_tg_bot()


if __name__ == '__main__':
    main()
