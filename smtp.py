import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart

import models


def send_to_kindle(user: models.User, message: MIMEMultipart) -> bool:
    ret = True
    try:
        server = smtplib.SMTP_SSL(os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT"))
        server.login(os.getenv("SMTP_USERNAME"), os.getenv("SMTP_PASSWORD"))
        server.sendmail(os.getenv("SMTP_USERNAME"), [user.emails[0].email, ], message.as_string())
        server.quit()
        user.log_send_email()
    except Exception as e:
        logging.getLogger().error(e)
        ret = False
    return ret
