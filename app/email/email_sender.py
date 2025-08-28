import logging
import smtplib
import time
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

    def smtp(self, to_email: str, email_content: MIMEMultipart, retries: int = 3, timeout: int = 15) -> bool:
        attempt = 0
        delay_seconds = 1
        # Normalize port to int with safe fallback
        try:
            port = int(self.port) if self.port else SMTP_SSL_PORT
        except Exception:
            port = SMTP_SSL_PORT

        while attempt < retries:
            try:
                if port == SMTP_SSL_PORT:
                    server = smtplib.SMTP_SSL(self.host, port, timeout=timeout)
                else:
                    server = smtplib.SMTP(self.host, port, timeout=timeout)
                    # Use STARTTLS when not using implicit SSL
                    try:
                        server.starttls()
                    except Exception:
                        pass
                server.login(self.username, self.password)
                server.sendmail(self.form_email or self.username, [to_email], email_content.as_string())
                server.quit()
                return True
            except Exception as e:
                logging.getLogger().error(e)
                attempt += 1
                if attempt >= retries:
                    break
                time.sleep(delay_seconds)
                delay_seconds = min(delay_seconds * 2, 10)
        return False


def send_to_kindle(email: str, message: MIMEMultipart, **kwargs) -> bool:
    email_sender = EmailSender(**kwargs)
    return email_sender.smtp(email, message)
