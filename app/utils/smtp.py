import logging
import smtplib
from email.mime.multipart import MIMEMultipart

from app.config.configs import smtp_config
from app.model.user import UserSendLog


def send_to_kindle(user_send_log: UserSendLog, message: MIMEMultipart) -> bool:
    ret = True
    try:
        server = smtplib.SMTP_SSL(smtp_config('host'), smtp_config("port"))
        server.login(smtp_config("username"), smtp_config("password"))
        server.sendmail(smtp_config("username"), [user_send_log.email, ], message.as_string())
        server.quit()
        user_send_log.send_succeed()
    except Exception as e:
        user_send_log.send_failed()
        logging.getLogger().error(e)
        ret = False
    return ret
