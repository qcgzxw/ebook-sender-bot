from playhouse.db_url import connect

from config.configs import default_config, telegram_config
from model.base import database_proxy
from model.user import User, UserEmail, UserSendLog
from tg_bot.tg_bot import TgBot, MessageReply


def register_db() -> None:
    # more information: http://docs.peewee-orm.com/en/latest/peewee/database.html#connecting-using-a-database-url
    database = connect(default_config('database'))
    database_proxy.initialize(database)
    database.create_tables([User, UserEmail, UserSendLog])


def run_tg_bot() -> None:
    bot_token = telegram_config('bot_token')
    develop_chat_id = telegram_config('developer_chat_id')
    bot = TgBot(bot_token, develop_chat_id)
    bot.run()


def main() -> None:
    register_db()
    run_tg_bot()


if __name__ == '__main__':
    main()
