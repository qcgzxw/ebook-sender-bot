from app.config.configs import telegram_config, database_config
from app.model.base import database_proxy
from app.model.user import User, UserEmail, UserSendLog
from app.tg_bot.tg_bot import TgBot


def register_db() -> None:
    database = database_config()
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
