import html
import json
import logging
import os
import shutil
import traceback
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import i18n

from telegram import Update, ParseMode, Bot
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from validate_email import validate_email

from config.configs import smtp_config, default_config
from model.user import User
from utils import util, smtp


class TgBot:
    token = None
    develop_chat_id = None
    reply = None
    lang = 'en-us'
    logger = None
    allow_file = ('doc', 'docx', 'rtf', 'html', 'htm', 'txt', 'mobi', 'pdf')
    allow_send_file = allow_file + ('azw', 'azw1', 'azw3', 'azw4', 'fb2', 'epub', 'lrf', 'kfx', 'pdb', 'lit')
    allow_email_domain = ('kindle.com', 'kindle.cn', )

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

    def command_start(self, update: Update, context: CallbackContext) -> None:
        User.find_or_create(update.message.from_user)
        self.reply.send_msg(update, 'start', email=smtp_config('username'))

    def command_help(self, update: Update, context: CallbackContext) -> None:
        self.reply.send_msg(update, 'help', email=smtp_config('username'))

    def command_email(self, update: Update, context: CallbackContext) -> None:
        """Set kindle email"""
        email = update.message.text
        user = User.find_or_create(update.message.from_user)
        if len(email.split()) == 1:
            if len(user.emails) == 0:
                self.reply.send_msg(update, 'emailErrorNotification')
            else:
                self.reply.send_msg(update, 'emailNotification', email=user.emails[0].email)
        else:
            email = email.split()[-1].lower()
            if validate_email(email) and (
                    user.is_developer()
                    or
                    email.split('@')[-1] in self.allow_email_domain
            ):
                user.set_email(email)
                self.reply.send_msg(update, 'emailSetNotification', email=smtp_config('username'))
            else:
                self.reply.send_msg(update, 'emailInvalidNotification')

    def document(self, update: Update, context: CallbackContext) -> None:
        """Handle document type message"""
        user = User.find_or_create(update.message.from_user)
        # check user email
        if len(user.emails) == 0:
            self.reply.send_msg(update, 'documentEmailError')
            return
        # check file type
        if update.message.document.file_name.split('.')[-1].lower() not in self.allow_send_file:
            self.reply.send_msg(update, 'documentFileTypeError', types="|.".join(self.allow_send_file))
            return
        # check file size
        if update.message.document.file_size == 0:
            self.reply.send_msg(update, 'documentFileEmptyError')
            return
        if not user.is_developer() and update.message.document.file_size > 20 * 1024 * 1024:
            self.reply.send_msg(update, 'documentFileSizeError')
            return
        if not user.is_developer() and int(default_config('email_send_limit')) < user.today_send_times():
            self.reply.send_msg(update, 'documentLimitError')
            return
        self.reply.send_msg(update, 'downloading')
        # download file
        save_path, exist = self.get_file_save_path(update)
        if not exist:
            with open(save_path, 'wb') as f:
                context.bot.get_file(update.message.document).download(out=f)
            if not os.path.exists(save_path):
                self.reply.send_msg(update, 'downloadFailed')
                return
        book_meta = util.get_book_meta(save_path)
        reply_msg = ""
        for key in book_meta.keys():
            if book_meta[key] != 'Unknown':
                reply_msg += f"<b>{key}:</b> <pre>{book_meta[key]}</pre>\r\n\r\n"
        if reply_msg == "":
            reply_msg = "sending..."
        self.reply.send_text(update, reply_msg)
        if os.path.exists(os.path.dirname(save_path) + os.sep + 'cover.png'):
            update.message.reply_photo(open(os.path.dirname(save_path) + os.sep + 'cover.png', 'rb'))
        if update.message.document.file_name.split('.')[-1] not in self.allow_file:
            # convert ebook to mobi
            util.convert_book_to_mobi(save_path)
        if smtp.send_to_kindle(user.log_send_email(update.message.document.file_unique_id), self.set_message(update, book_meta)):
            self.reply.send_msg(update, 'done')
        else:
            self.reply.send_msg(update, 'sendFailed')
        # todo: add to queue
        if book_meta['Title'] != "Unknown" and len(book_meta['Title'].encode()) <= 200:
            fp, _ = self.get_file_save_path(update)
            ext = os.path.splitext(fp)[1]
            if os.path.exists(os.path.splitext(fp)[0] + ".mobi"):
                fp = os.path.splitext(fp)[0] + ".mobi"
                ext = ".mobi"
            new_path = os.getcwd() + os.sep + "books" + os.sep
            if book_meta['Author(s)'] != "Unknown" and \
                    len(book_meta['Author(s)'].encode()) + len(book_meta['Title'].encode()) <= 250:
                new_path += book_meta['Author(s)'] + " - "
            new_path += book_meta['Title']
            new_path += ext
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            if not os.path.exists(new_path):
                shutil.copy(fp, new_path)

    @staticmethod
    def get_file_save_path(update: Update) -> (str, bool):
        save_path = os.getcwd() + os.sep \
                    + "storage" + os.sep \
                    + str(update.message.from_user.id) + os.sep \
                    + update.message.document.file_unique_id + os.sep \
                    + update.message.document.file_name
        if not os.path.exists(os.path.dirname(save_path)):
            os.makedirs(os.path.dirname(save_path))
        is_file_exist = os.path.exists(save_path)
        return save_path, is_file_exist

    @staticmethod
    def set_message(update: Update, book_meta) -> MIMEMultipart:
        file_name = update.message.document.file_name
        file_path, _ = TgBot.get_file_save_path(update)
        if file_name.split('.')[-1].lower() != "mobi" and os.path.exists(os.path.splitext(file_path)[0] + ".mobi"):
            file_path = os.path.splitext(file_path)[0] + ".mobi"
            file_name = os.path.splitext(file_name)[0] + ".mobi"
        user = User.find_or_create(update.message.from_user)
        message = MIMEMultipart()
        message['From'] = smtp_config('username')
        message['To'] = user.emails[0].email
        subject = file_name
        message['Subject'] = Header(subject, 'utf-8')
        body = book_meta['Title'] if book_meta['Title'] != "Unknown" else file_name
        if book_meta['Author(s)'] != "Unknown":
            body += f"\r\nBy:{book_meta['Author(s)']}"
        if book_meta['Published'] != "Unknown":
            body += f"\r\nAt:{book_meta['Published']}"
        msg_text = MIMEText(body, 'plain', 'utf-8')
        message.attach(msg_text)
        with open(file_path, 'rb') as f:
            att = MIMEApplication(f.read())
            att.add_header(
                'Content-Disposition',
                'attachment',
                filename=Header(file_name, "utf-8").encode())
            message.attach(att)
        return message

    def run(self):
        updater = Updater(self.token)
        dispatcher = updater.dispatcher
        self.reply = MessageReply(self.token)

        # Register the commands...
        dispatcher.add_handler(CommandHandler('start', self.command_start))
        dispatcher.add_handler(CommandHandler('help', self.command_help))
        dispatcher.add_handler(CommandHandler('email', self.command_email))
        dispatcher.add_handler(CommandHandler('github', self.command_github))
        dispatcher.add_handler(MessageHandler(Filters.document, self.document))

        # Send debug information to develop
        dispatcher.add_error_handler(self.error_handler)

        updater.start_polling()
        updater.idle()


class MessageReply:
    bot = None
    chat_id = None

    def __init__(self, bot_token):
        self.bot = Bot(bot_token)
        i18n.load_path.append('lang')
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
