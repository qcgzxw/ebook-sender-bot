import html
import json
import logging
import os
import traceback
from email import encoders
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from telegram import Update, ParseMode
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from validate_email import validate_email

import models
import smtp


class TgBot:
    token = None
    develop_chat_id = None
    lang = 'en-us'
    logger = None
    menus = ['/start', '/help', '/email']
    allow_file = ('doc', 'docx', 'rtf', 'html', 'htm', 'txt', 'zip', 'mobi', 'pdf')

    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.develop_chat_id = chat_id
        if os.getenv("DEV", "False") == "True":
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        else:
            logging.basicConfig(level=logging.ERROR,
                                format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger("telegram_message")

    def error_handler(self, update: Update, context: CallbackContext) -> None:
        """Log the error and send a telegram message to notify the developer."""
        # Log the error before we do anything else, so we can see it even if something breaks.
        self.logger.error(msg="Exception while handling an update:", exc_info=context.error)
        # Send the error to user
        if update is not None:
            update.message.reply_text(
                f"<b>Error</b>:\r\n<pre> {context.error} </pre>\r\n\r\n"
                + "<b>Contact us at</b>:\r\n"
                + "<a href='https://github.com/qcgzxw/ebook-sender-bot/issues'>https://github.com/qcgzxw/ebook-sender"
                  "-bot/issues</a> ", parse_mode=ParseMode.HTML)
        if self.develop_chat_id is not None:
            # traceback.format_exception returns the usual python message about an exception, but as a
            # list of strings rather than a single string, so we have to join them together.
            tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
            tb_string = ''.join(tb_list)

            # Build the message with some markup and additional information about what happened.
            # You might need to add some logic to deal with messages longer than the 4096 character limit.
            update_str = update.to_dict() if isinstance(update, Update) else str(update)
            message = (
                f'An exception was raised while handling an update\n'
                f'<pre>update = {html.escape(json.dumps(update_str, indent=2, ensure_ascii=False))}'
                '</pre>\n\n'
                f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
                f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
                f'<pre>{html.escape(tb_string)}</pre>'
            )
            context.bot.send_message(chat_id=self.develop_chat_id, text=message, parse_mode=ParseMode.HTML)

    def command_github(self, update: Update, context: CallbackContext) -> None:
        update.message.reply_text(
            "<b>Github: </b>\r\n"
            + "<a href='https://github.com/qcgzxw/ebook-sender-bot'>qcgzxw/ebook-sender-bot</a>"
            + "\r\n"
            + "\r\n"
            + "<b>Issue: </b>\r\n"
            + "<a href='https://github.com/qcgzxw/ebook-sender-bot/issues'>https://github.com/qcgzxw/ebook-sender-bot"
              "/issues</a> "
            , parse_mode=ParseMode.HTML
        )

    def command_start(self, update: Update, context: CallbackContext) -> None:
        models.User.find_or_create(update.message.from_user)
        update.message.reply_text(
            "First, set your <b>Send-to-Kindle e-mail</b> by send command\r\n"
            "<code>/email send-to-kindle-email@kindle.com</code>.\r\n"
            "You can get more send<code>/help</code>."
            , parse_mode=ParseMode.HTML
        )

    def command_help(self, update: Update, context: CallbackContext) -> None:
        # todo: i18n
        # user_lang = (update.message.from_user.language_code or "en-us").lower()
        update.message.reply_text(
            "<b>What does this bot do?</b>\r\n"
            + "This bot is able to send documents to your Kindle by e-mailing the documents to your <b>Send-to-Kindle "
            + "e-mail</b> address."
            + "\r\n"
            + "\r\n"
            + "<b>Where is my Kindle's e-mail?</b>\r\n"
            + "Log into your Amazon account. Visit <i>Manage Your Content and Devices</i> page at <a "
            + "href='https://www.amazon.com/hz/mycd/myx#/home/settings/payment'>Preferences</a>.\r\n "
            + "The e-mail address will end with <code>@kindle.com</code>."
            + "\r\n"
            + "\r\n"
            + "<b>How to set the <i>Approved Personal Document E-mail</i>?</b>\r\n"
            + "You can find this setting in <a href='https://www.amazon.com/hz/mycd/myx#/home/settings/payment'>"
            + "Preferences</a>.\r\n"
            + "Then add this bot's email: <code>"
            + os.getenv("SMTP_USERNAME")
            + "</code>\r\n to the list otherwise you'll not be able to use this bot."
            + "\r\n"
            + "\r\n"
            + "<b>Github: </b>\r\n"
            + "<a href='https://github.com/qcgzxw/ebook-sender-bot'>qcgzxw/ebook-sender-bot</a>"
            , parse_mode=ParseMode.HTML
        )

    def command_email(self, update: Update, context: CallbackContext) -> None:
        """Set kindle email"""
        reply_msg = "Please, check your e-mail and try again."
        email = update.message.text
        if email:
            if len(email.split()) == 1:
                reply_msg = "Send: \r\n" \
                            "<code>/email send-to-kindle-email@kindle.com</code>\r\n" \
                            "to set your kindle email."
            else:
                email = email.split()[-1].lower()
                if validate_email(email) and (email.endswith("@kindle.com") or email.endswith("@kindle.cn")):
                    user = models.User.find_or_create(update.message.from_user)
                    user.set_email(email)
                    reply_msg = "New email set.\r\n" \
                                "Then add : <code>" + os.getenv("SMTP_USERNAME") + "</code>\r\n" \
                                + "to the <a href='https://www.amazon.com/hz/mycd/myx#/home/settings/payment" \
                                  "'>Approved Personal Document Email List</a>"\
                                + "\r\n" \
                                + "\r\n" \
                                + "<a href='https://www.amazon.com/gp/help/customer/display.html?nodeId" \
                                  "=GX9XLEVV8G4DB28H'>Add an Email Address to Receive Documents in Your Kindle " \
                                  "Library</a>"

        update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)

    def document(self, update: Update, context: CallbackContext) -> None:
        """Handle document type message"""
        user = models.User.find_or_create(update.message.from_user)
        # check user email
        if len(user.emails) == 0:
            reply_msg = "Please, send <b>/email</b> to set your e-mail and try again."
            update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)
            return
        # check file type
        if update.message.document.file_name.split(".")[-1] not in self.allow_file:
            reply_msg = "You can only send [." + "|.".join(self.allow_file) + "] files to your kindle."
            update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)
            return
        # check file size
        if update.message.document.file_size == 0 or update.message.document.file_size > 50 * 1024 * 1024:
            reply_msg = "File[up to 50MB] too large."
            update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)
            return
        if self.develop_chat_id != update.message.from_user.id \
                and int(os.getenv("EMAIL_SEND_LIMIT", 0)) < user.today_send_times():
            reply_msg = "You have sent too many times today, you may try tomorrow."
            update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)
            return
        reply_msg = "Downloading..."
        update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)
        # download file
        save_path, exist = self.get_file_save_path(update)
        if not exist:
            with open(save_path, 'wb') as f:
                context.bot.get_file(update.message.document).download(out=f)
            if not os.path.exists(save_path):
                reply_msg = "Download failed."
                update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)
                return
        reply_msg = "Sending..."
        update.message.reply_text(reply_msg, parse_mode=ParseMode.HTML)
        if smtp.send_to_kindle(user, self.set_message(update)):
            update.message.reply_text("Done.You can check if this file can be found on your kindle!")
        else:
            update.message.reply_text("Sending failed!")
        # todo: send document info
        # todo: convert books
        # todo: add to queue

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
    def set_message(update: Update) -> MIMEMultipart:
        file_path, _ = TgBot.get_file_save_path(update)
        user = models.User.find_or_create(update.message.from_user)
        message = MIMEMultipart()
        message['From'] = os.getenv("SMTP_USERNAME")
        message['To'] = user.emails[0].email
        subject = update.message.document.file_name
        message['Subject'] = Header(subject, 'utf-8')
        msg_text = MIMEText('This attach is from Ebook-Send-Bot.', 'plain', 'utf-8')
        message.attach(msg_text)
        with open(file_path, 'rb') as f:
            attachment = MIMEText(f.read(), 'base64', 'utf-8')
            attachment["Content-Type"] = 'application/epub'
            attachment.add_header("Content-Disposition", "attachment", filename=('utf-8', '', subject))
            encoders.encode_base64(attachment)
            message.attach(attachment)
        return message

    def run(self):
        updater = Updater(self.token)
        dispatcher = updater.dispatcher

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
