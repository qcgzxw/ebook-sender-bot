import os

from dotenv import load_dotenv

import models
from tg_bot import TgBot


def register_db() -> None:
    models.database.create_tables([models.User, models.UserEmail, models.UserSendLog])


def run_tg_bot() -> None:
    bot_token = os.getenv('TELEGRAM_TOKEN')
    develop_chat_id = os.getenv('TELEGRAM_DEVELOP_CHAT_ID')
    bot = TgBot(bot_token, develop_chat_id)
    bot.run()


def main() -> None:
    load_dotenv()
    register_db()
    run_tg_bot()


if __name__ == '__main__':
    main()
