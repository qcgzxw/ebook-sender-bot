import email
import os
import shutil
from email import encoders
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import telegram

from app.config.configs import default_config
from app.tg_bot.errors import NotifyException
from app.tg_bot.user import User
from app.email.email_sender import send_to_kindle
from app.utils.util import convert_book, get_book_meta


class Document:
    amazon_allow_file = ('doc', 'docx', 'rtf', 'html', 'htm', 'pdf', 'txt', 'epub')
    allow_send_file = amazon_allow_file + \
                      ('azw', 'azw1', 'azw3', 'azw4', 'fb2', 'lrf', 'kfx', 'pdb', 'lit', 'mobi')

    user: User
    origin_file: telegram.Document = None
    origin_file_path: str = ''
    new_file_path: str = ''
    book_meta: dict = None

    def __init__(self, document: telegram.Document, user: User):
        user.check()
        self.user = user
        self.origin_file = document

        self.origin_file_path = os.sep.join([
            os.getcwd(),
            "storage",
            str(self.user.user_model.telegram_id),
            self.origin_file.file_unique_id,
            self.origin_file.file_name
        ])
        self.check()

    def check(self):
        self._check_file()
        self._check_total_send()

    def _check_file(self):
        if self.origin_file.file_name.split('.')[-1].lower() not in self.allow_send_file:
            raise NotifyException('documentFileTypeError', "|.".join(self.allow_send_file))

        if self.origin_file.file_size == 0:
            raise NotifyException('documentFileEmptyError')

        if not self.user.is_develop():
            if self.origin_file.file_size > 20 * 1024 * 1024:
                raise NotifyException('documentFileSizeError')

    def _check_total_send(self):
        if not self.user.is_develop() or not self.user.is_vip():
            if 0 < int(default_config('email_send_limit')) < self.user.get_today_send_times():
                raise NotifyException('documentLimitError')

    def save_file(self, get_file_func):
        if not os.path.exists(os.path.dirname(self.origin_file_path)):
            os.makedirs(os.path.dirname(self.origin_file_path))
        if not os.path.exists(self.origin_file_path):
            with open(self.origin_file_path, 'wb') as f:
                get_file_func.download(out=f)
            if not os.path.exists(self.origin_file_path):
                raise NotifyException('downloadFailed')

    def get_book_meta(self) -> dict:
        if self.book_meta is None:
            self.book_meta = get_book_meta(self.origin_file_path)
        return self.book_meta

    def _convert_file(self):
        if self.origin_file.file_name.split('.')[-1].lower() in self.amazon_allow_file:
            self.new_file_path = self.origin_file_path
            return
        if not self.user.is_vip() and not self.user.is_develop():
            raise NotifyException('eBookConvertIsForVip')
        success, self.new_file_path = convert_book(self.origin_file_path)
        if not success or self.new_file_path == '':
            raise NotifyException('documentFileConvertError')

        if os.path.getsize(self.new_file_path) > 50 * 1024 * 1024:
            raise NotifyException('documentFileSizeError')

    def send_file_to_kindle(self):
        self._convert_file()
        file_name = os.path.basename(self.new_file_path)
        book_meta = self.get_book_meta()

        def get_message() -> MIMEMultipart:
            message = MIMEMultipart()
            message['From'] = self.user.get_sender()
            message['To'] = self.user.get_email()
            message['Subject'] = Header(file_name, 'utf-8')
            message['Date'] = email.utils.formatdate()
            message['Message-ID'] = email.utils.make_msgid(self.user.get_email())
            body = book_meta['Title'] if book_meta['Title'] != "Unknown" else file_name
            if book_meta['Author(s)'] != "Unknown":
                body += f"\r\nBy:{book_meta['Author(s)']}"
            if book_meta['Published'] != "Unknown":
                body += f"\r\nAt:{book_meta['Published']}"
            msg_text = MIMEText(body, 'plain', 'utf-8')
            message.attach(msg_text)
            with open(self.new_file_path, 'rb') as f:
                att = MIMEApplication(f.read())
                att.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=Header(file_name, "utf-8").encode()
                )
                encoders.encode_base64(att)
                message.attach(att)
            return message

        user_send_log = self.user.user_model.log_send_email(
            self.user.get_sender(),
            self.origin_file.file_unique_id
        )
        if not send_to_kindle(
            self.user.get_email(),
            get_message(),
            **self.user.get_email_config()
        ):
            user_send_log.send_failed()
            raise NotifyException("sendFailed")
        user_send_log.send_succeed()

    def copy_file_to_storage(self):
        book_meta = self.get_book_meta()
        if book_meta['Title'] != "Unknown" and len(book_meta['Title'].encode()) <= 200:
            ext = os.path.splitext(self.new_file_path)[1]
            new_path = os.getcwd() + os.sep + "books" + os.sep
            if book_meta['Author(s)'] != "Unknown" and \
                    len(book_meta['Author(s)'].encode()) + len(book_meta['Title'].encode()) <= 250:
                new_path += book_meta['Author(s)'] + " - "
            new_path += book_meta['Title']
            new_path += ext
            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))
            if not os.path.exists(new_path):
                shutil.copy(self.new_file_path, new_path)
