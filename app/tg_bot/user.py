import datetime
import json
import typing

import telegram
from validate_email import validate_email
from app.config.configs import default_config, provider_config, smtp_config

from app.model.user import User as UserModel
from app.model.user import get_send_history
from app.tg_bot.errors import NotifyException
from app.src.mailcow_api.mailcow_api import MailcowApi


class User:
    allow_email_domain = (
        'kindle.com', 'kindle.cn', 'kindle.co.uk', 'kindle.fr', 'kindle.de', 'kindle.it', 'kindle.co.jp', 'kindle.ca',
        'kindle.nl', 'kindle.pl', 'kindle.es', 'kindle.sg', 'kindle.com.au', 'kindle.com.br', 'kindle.in',
        'kindle.com.mx',
        'kindle.com.tr', 'kindle.ae'
    )

    user_model: UserModel = None
    email: str = ''
    sender_email: str = ''

    def __init__(self, user: telegram.User):
        self.user_model = UserModel.find_or_create(user)
        if len(self.user_model.emails) > 0:
            self.email = self.user_model.emails[0].email
            self.sender_email = self.user_model.emails[0].sender_email

    def get_email(self) -> str:
        return self.email

    def is_vip(self) -> bool:
        if default_config('vip').lower() == 'true':
            return self.user_model.is_vip
        return True

    def get_sender(self) -> str:
        return self.sender_email

    def create_email_sender(self) -> bool:
        if default_config('email_provider') == 'config':
            return True
        elif default_config('email_provider') == 'mailcow' or default_config('email_provider') == 'mailcow_alias':
            self.user_model.set_email_sender()
            return self.user_model.emails[0].sender_email_created == 1
        else:
            return False

    def get_email_config(self) -> typing.Union[dict, None]:
        if default_config('email_provider') == 'mailcow':
            user_email = self.user_model.emails[0]
            if user_email.sender_email != "" and user_email.sender_email_created:
                return {
                    'username': user_email.sender_email,
                    'password': user_email.sender_email_password,
                    'host': provider_config('mailcow_mailbox_domain')
                }
        elif default_config('email_provider') == 'config':
            return {
                'username': smtp_config('username'),
                'password': smtp_config('password'),
                'host': smtp_config('host'),
                'port': smtp_config('port'),
            }
        elif default_config('email_provider') == 'mailcow_alias':
            user_email = self.user_model.emails[0]
            return {
                'username': smtp_config('username'),
                'form_email': user_email.sender_email,
                'password': smtp_config('password'),
                'host': smtp_config('host'),
                'port': smtp_config('port'),
            }
        return None

    def check(self):
        if self.email == '':
            raise NotifyException('documentEmailError')

    def is_develop(self) -> bool:
        return self.user_model.is_developer()

    def get_today_send_times(self) -> int:
        return self.user_model.today_send_times()

    def create_sender_email(self):
        mailcow = MailcowApi(provider_config('mailcow_url'), provider_config('mailcow_api_key'))
        if default_config('email_provider') == 'mailcow':
            sender_email = self.user_model.emails[0].sender_email
            sender_email_password = self.user_model.emails[0].sender_email_password
            if sender_email and sender_email != '' and self.user_model.emails[0].sender_email_created == 0:
                data = mailcow.get_mailboxes(str(sender_email))
                if not data:
                    created, data = mailcow.register_mailbox(
                        sender_email,
                        sender_email_password,
                        fullname=self.user_model.nickname
                    )
                    if created:
                        self.user_model.log_created_email()
                        return
                else:
                    raise Exception("email exists")
        elif default_config('email_provider') == 'mailcow_alias':
            sender_email = self.user_model.emails[0].sender_email
            if sender_email and sender_email != '' and self.user_model.emails[0].sender_email_created == 0:
                added, data = mailcow.add_aliases(
                    sender_email,
                    smtp_config('username')
                )
                if added or (type(data) is list and data[0] == 'is_alias_or_mailbox'):
                    self.user_model.log_created_email()
                    return
                else:
                    raise Exception(data)

    def set_email(self, email: str = '') -> str:
        if email == '':
            if self.email == '':
                raise NotifyException('emailErrorNotification')
            else:
                raise NotifyException('emailNotification', self.email)

        if validate_email(email) and email != "email@kindle.com" and (
            self.is_develop() or email.split('@')[-1] in self.allow_email_domain
        ):
            self.user_model.set_email(email)
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
