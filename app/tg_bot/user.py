import telegram
from validate_email import validate_email

from app.model.user import User as UserModel
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
