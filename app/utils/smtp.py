import logging
import smtplib
from email.mime.multipart import MIMEMultipart

from app.config.configs import smtp_config


def send_to_kindle(email: str, message: MIMEMultipart) -> bool:
    ret = True
    try:
        server = smtplib.SMTP_SSL(smtp_config('host'), smtp_config("port"))
        server.login(smtp_config("username"), smtp_config("password"))
        server.sendmail(smtp_config("username"), [email, ], message.as_string())
        server.quit()
    except Exception as e:
        logging.getLogger().error(e)
        ret = False
    return ret
