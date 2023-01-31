import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from app.config.configs import smtp_config
SMTP_DEFAULT_PORT = 25
SMTP_SSL_PORT = 465
SMTP_TLS_PORT = 587


class EmailSender:
    host = ''
    username = ''
    form_email = ''
    port = SMTP_SSL_PORT
    password = ''

    def __init__(self, **kwargs):
        self.host = kwargs.get('host', smtp_config('host'))
        self.username = kwargs.get('username', smtp_config('username'))
        self.form_email = kwargs.get('form_email', self.username)
        self.port = kwargs.get('port', smtp_config('port'))
        self.password = kwargs.get('password', smtp_config('password'))

    def smtp(self, to_email: str, email_content: MIMEMultipart) -> bool:
        ret = True
        try:
            server = smtplib.SMTP_SSL(self.host, self.port)
            server.login(self.username, self.password)
            server.sendmail(self.form_email, [to_email, ], email_content.as_string())
            server.quit()
        except Exception as e:
            logging.getLogger().error(e)
            ret = False
        return ret


def send_to_kindle(email: str, message: MIMEMultipart, **kwargs) -> bool:
    email_sender = EmailSender(**kwargs)
    return email_sender.smtp(email, message)
