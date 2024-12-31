import datetime
import html
import json
import logging
import time
import traceback

import i18n
import pytz
import tzlocal
from telegram import Update, ParseMode, Bot
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters

from app.config.configs import default_config
from app.model.user import UserEmail
from app.tg_bot.document import Document
from app.tg_bot.errors import NotifyException
from app.tg_bot.user import User
from app.utils.util import gen_sender_email_username


class TgBot:
    token = None
    develop_chat_id = None
    reply = None
    lang = 'en-us'
    logger = None

    maintenance_end_timestamp = 0

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.develop_chat_id = chat_id
        if default_config('mode') == 'dev':
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        else:
            logging.basicConfig(level=logging.ERROR,
                                format='%(asctime)s - %(message)s - %(levelname)s - %(message)s',
                                handlers=[logging.FileHandler(filename='default.log', mode='a', encoding='utf-8')],
                                )
        self.logger = logging.getLogger("telegram_message")

    def error_handler(self, update: Update, context: CallbackContext) -> None:
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        self.logger.error(msg="Exception while handling an update:", exc_info=context.error)
        # Send the error to user
        self.reply.send_msg(update, msg_type='error', err_msg=context.error)
        if self.develop_chat_id is not None:
            # traceback.format_exception returns the usual python message about an exception, but as a
            # list of strings rather than a single string, so we have to join them together.
            tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
            tb_string = ''.join(tb_list)

            # Build the message with some markup and additional information about what happened.
            # You might need to add some logic to deal with messages longer than the 4096 character limit.
            update_str = update.to_dict() if isinstance(update, Update) else str(update)
            self.reply.send_msg(
                update,
                'developError',
                update_data=html.escape(json.dumps(update_str, indent=2, ensure_ascii=False)),
                chat_data=html.escape(str(context.chat_data)),
                user_data=html.escape(str(context.user_data)),
                err_msg=html.escape(tb_string),
                chat_id=self.develop_chat_id,
            )

    def command_github(self, update: Update, context: CallbackContext) -> None:
        self.reply.send_msg(update, 'github')

    def command_donate(self, update: Update, context: CallbackContext) -> None:
        self.reply.send_msg(update, 'donate')

    def command_start(self, update: Update, context: CallbackContext) -> None:
        User(update.message.from_user)
        self.reply.send_msg(update, 'start', email=gen_sender_email_username(update.message.from_user.id))

    def is_in_maintenance_mode(self):
        return self.maintenance_end_timestamp > 0

    def check_perm(command_func):
        def command_warp(*args, **kwargs):
            def command(self, update: Update, context: CallbackContext):
                if self.is_in_maintenance_mode():
                    return self.command_maintenance(update, context)
                user = User(update.message.from_user)
                if not user.create_email_sender():
                    user.create_sender_email()
                    self.reply.send_msg(update, 'email_confirm', email=gen_sender_email_username(update.message.from_user.id))
                    return
                return command_func(self, update, context)

            return command(*args, **kwargs)

        return command_warp

    def is_admin(command_func):
        def command_warp(*args, **kwargs):
            def command(self, update: Update, context: CallbackContext):
                user = User(update.message.from_user)
                if user.is_develop():
                    return command_func(self, user, update, context)

            return command(*args, **kwargs)

        return command_warp

    @is_admin
    def command_admin(self, user: User, update: Update, context: CallbackContext) -> None:
        self.reply.send_msg(update, 'adminCommand')

    @is_admin
    def command_test(self, user: User, update: Update, context: CallbackContext) -> None:
        if len(update.message.text.split()) == 1:
            command = ""
        else:
            command = update.message.text.split()[1]
        if command != "":
            self.reply.send_msg(update, command)

    @is_admin
    def command_daily_stats(self, user: User, update: Update, context: CallbackContext) -> None:
        update.message.reply_markdown(text=str(user.get_daily_stats()))

    @is_admin
    def command_monthly_stats(self, user: User, update: Update, context: CallbackContext) -> None:
        update.message.reply_markdown(text=str(user.get_monthly_stats()))

    @is_admin
    def command_stats(self, user: User, update: Update, context: CallbackContext) -> None:
        update.message.reply_markdown(text=str(user.get_stats()))

    @is_admin
    def enable_maintenance(self, user: User, update: Update, context: CallbackContext) -> None:
        if len(update.message.text.split()) > 1 and update.message.text.split()[1].isnumeric():
            end_time = int(update.message.text.split()[1])
        else:
            end_time = int(time.time()) + 10 * 60
        self.maintenance_end_timestamp = end_time
        self.reply.send_msg(update, 'enableMaintenanceModeNotification')

    @is_admin
    def disable_maintenance(self, user: User, update: Update, context: CallbackContext) -> None:
        self.maintenance_end_timestamp = 0
        self.reply.send_msg(update, 'disableMaintenanceModeNotification')

    @is_admin
    def set_vip(self, user: User, update: Update, context: CallbackContext) -> None:
        parts = update.message.text.split()
        if len(parts) != 2:
            self.reply.send_msg(update, 'emailRequiredNotification')
            return
        email = parts[1]
        user_email = UserEmail.get_or_none(UserEmail.email == email)
        if not user_email or not user_email.user:
            self.reply.send_msg(update, "unknownEmailAddress")
            return
        target_user = user_email.user
        # 设置用户为VIP
        target_user.set_vip(True)
        self.reply.send_msg(update, "setVipSuccess")
        self.reply.send_msg(
            update,
            'becomeVipMemberMessage',
            chat_id=target_user.telegram_id,
        )

    def command_help(self, update: Update, context: CallbackContext) -> None:
        self.reply.send_msg(update, 'help', email=gen_sender_email_username(update.message.from_user.id))

    def command_maintenance(self, update: Update, context: CallbackContext) -> None:
        maintenance_end_time = datetime.datetime.fromtimestamp(self.maintenance_end_timestamp)
        system_tz = tzlocal.get_localzone_name()
        self.reply.send_msg(
            update,
            'maintenanceHelp',
            end_time=maintenance_end_time.astimezone(pytz.timezone(system_tz)).strftime("%Y-%m-%d %H:%M %Z (%z)")
        )

    @check_perm
    def command_email(self, update: Update, context: CallbackContext) -> None:
        """Set kindle email"""
        user = User(update.message.from_user)
        if len(update.message.text.split()) == 1:
            email = ""
        else:
            email = update.message.text.split()[1]
        try:
            user.set_email(email)
            self.reply.send_msg(
                update,
                'emailSetNotification',
                email=gen_sender_email_username(update.message.from_user.id)
            )
        except NotifyException as e:
            if e.args is not None:
                if e.args[0] == "emailNotification":
                    self.reply.send_msg(update, e.args[0], email=e.args[1])
                else:
                    self.reply.send_msg(update, e.args[0])
        except Exception as e:
            raise e

    @check_perm
    def document(self, update: Update, context: CallbackContext) -> None:
        """Handle document type message"""
        try:
            document = Document(update.message.document, User(update.message.from_user))
            self.reply.send_msg(update, 'downloading')
            document.save_file(context.bot.get_file(update.message.document))
            document.get_book_meta()

            def send_book_meta(book_meta: dict):
                if book_meta.get('cover_path') is not None:
                    try:
                        update.message.reply_photo(open(book_meta['cover_path'], 'rb'))
                    except Exception:
                        pass
                        # update.message.reply_markdown(text=str(e))
                    del book_meta['cover_path']
                reply_msg = ""
                for key in book_meta.keys():
                    if book_meta[key] != 'Unknown' and len(book_meta[key]) < 4000:
                        reply_msg += f"<b>{key}:</b> <pre>{book_meta[key]}</pre>\r\n\r\n"
                if reply_msg == "":
                    reply_msg = "sending..."
                self.reply.send_text(update, reply_msg)

            send_book_meta(document.get_book_meta())
            document.send_file_to_kindle()
            self.reply.send_msg(update, 'done')
            document.copy_file_to_storage()

        except NotifyException as e:
            if e.args is not None:
                if e.args[0] == "documentFileTypeError":
                    self.reply.send_msg(update, e.args[0], types=e.args[1])
                else:
                    self.reply.send_msg(update, e.args[0])
        except Exception as e:
            raise e

    def run(self):
        updater = Updater(self.token)
        dispatcher = updater.dispatcher
        self.reply = MessageReply(self.token)

        # Register the commands...
        dispatcher.add_handler(CommandHandler('start', self.command_start))
        dispatcher.add_handler(CommandHandler('help', self.command_help))
        dispatcher.add_handler(CommandHandler('email', self.command_email))
        #dispatcher.add_handler(CommandHandler('github', self.command_github))
        dispatcher.add_handler(CommandHandler('donate', self.command_donate))
        dispatcher.add_handler(MessageHandler(Filters.document, self.document))

        # Admin command
        dispatcher.add_handler(CommandHandler('test', self.command_test))
        dispatcher.add_handler(CommandHandler('admin', self.command_admin))
        dispatcher.add_handler(CommandHandler('daily_stats', self.command_daily_stats))
        dispatcher.add_handler(CommandHandler('monthly_stats', self.command_monthly_stats))
        dispatcher.add_handler(CommandHandler('stats', self.command_stats))
        dispatcher.add_handler(CommandHandler('enable_maintenance', self.enable_maintenance))
        dispatcher.add_handler(CommandHandler('disable_maintenance', self.disable_maintenance))
        dispatcher.add_handler(CommandHandler('set_vip', self.set_vip))

        # Send debug information to develop
        dispatcher.add_error_handler(self.error_handler)

        updater.start_polling()
        updater.idle()


class MessageReply:
    bot = None
    chat_id = None

    def __init__(self, bot_token):
        self.bot = Bot(bot_token)
        i18n.load_path.append('app/lang')
        i18n.set('fallback', 'en-us')

    def send_msg_decorator(func):
        def send_msg(self, *args, **kwargs):
            msg = func(self, *args, **kwargs)
            if msg is not None:
                self.bot.send_message(
                    text=msg,
                    chat_id=self.chat_id,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )

        return send_msg

    @send_msg_decorator
    def send_msg(self, update: Update, msg_type: str, **kwargs):
        if update is None or (update.message.from_user.id is None and 'chat_id' not in kwargs.keys()):
            return None
        self.chat_id = update.message.from_user.id if 'chat_id' not in kwargs.keys() else kwargs.get('chat_id')
        i18n.set('locale', update.message.from_user.language_code.lower())
        return i18n.t(f'bot.{msg_type}', **kwargs)

    @send_msg_decorator
    def send_text(self, update: Update, msg: str):
        if update is None or update.message.from_user.id is None:
            return None

        return msg
