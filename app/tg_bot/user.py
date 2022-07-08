import datetime

import telegram
from validate_email import validate_email

from app.model.user import User as UserModel
from app.model.user import get_send_history
from app.tg_bot.errors import NotifyException


class User:
    allow_email_domain = (
        'kindle.com', 'kindle.cn', 'kindle.co.uk', 'kindle.fr', 'kindle.de', 'kindle.it', 'kindle.co.jp', 'kindle.ca',
        'kindle.nl', 'kindle.pl', 'kindle.es', 'kindle.sg', 'kindle.com.au', 'kindle.com.br', 'kindle.in',
        'kindle.com.mx',
        'kindle.com.tr', 'kindle.ae'
    )

    userModel: UserModel = None
    email: str = ''

    def __init__(self, user: telegram.User):
        self.userModel = UserModel.find_or_create(user)
        if len(self.userModel.emails) > 0:
            self.email = self.userModel.emails[0].email

    def check(self):
        if self.email == '':
            raise NotifyException('documentEmailError')

    def is_develop(self) -> bool:
        return self.userModel.is_developer()

    def get_today_send_times(self) -> int:
        return self.userModel.today_send_times()

    def set_email(self, email: str = '') -> str:
        if email == '':
            if self.email == '':
                raise NotifyException('emailErrorNotification')
            else:
                raise NotifyException('emailNotification', self.email)

        if validate_email(email) and email != "send-to-kindle-email@kindle.com" and (
            self.is_develop() or email.split('@')[-1] in self.allow_email_domain
        ):
            self.userModel.set_email(email)
            self.email = email
        else:
            raise NotifyException('emailInvalidNotification')

        return self.email

    def get_daily_stats(self):
        return self.get_stats(datetime.date.today())

    def get_monthly_stats(self):
        return self.get_stats(datetime.datetime(datetime.date.today().year, datetime.date.today().month, 1))

    def get_stats(self, start_time=None):
        def build_stats_msg(results) -> str:
            msg = ''
            for item in results:
                msg += '*' + item['username'] + '*: ' + str(item['num_logs']) + '\r\n'
            if msg == '':
                msg = 'No record.'
            return msg
        return build_stats_msg(get_send_history(start_time))
