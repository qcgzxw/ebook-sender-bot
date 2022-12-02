import json

from .mailcow_helper import MailcowHelper



MAILBOXES_GET_MAILBOXES = 'get/mailbox/'
MAILBOXES_CREATE_MAILBOX = 'add/mailbox'
DEFAULT_MAILBOX_QUOTA = '1'
DEFAULT_MAILBOX_FORCE_PASSWORD_UPDATE = '0'
DEFAULT_MAILBOX_FORCE_TLS_IN = '1'
DEFAULT_MAILBOX_FORCE_TLS_OUT = '1'
DEFAULT_MAILBOX_TAGS = ['ebook-sender']


class MailcowApiException(Exception):
    pass


class MailcowApi:

    mailcow_instance = None

    def __init__(self, api_url: str, api_key: str):
        if api_url != "" and api_key != "":
            self.mailcow_instance = MailcowHelper(api_url=api_url, api_key=api_key)

    def _get_instance(self) -> MailcowHelper:
        if self.mailcow_instance is None:
            raise MailcowApiException('Mailbox instance not initialized')
        return self.mailcow_instance

    def register_mailbox(self, username: str, password: str, **kwargs) -> (bool, object):
        if self.mailcow_instance is None:
            raise MailcowApiException('Mailbox instance not initialized')

        if '@' not in username:
            raise MailcowApiException('params invalid')

        u = username.split('@')[0]
        d = username.split('@')[1]

        data = {
            "active": "1",
            "domain": d,
            "local_part": u,
            "name": kwargs.get('fullname', u),
            "password": password,
            "password2": password,
            "quota": DEFAULT_MAILBOX_QUOTA,
            "force_pw_update": DEFAULT_MAILBOX_FORCE_PASSWORD_UPDATE,
            "tls_enforce_in": DEFAULT_MAILBOX_FORCE_TLS_IN,
            "tls_enforce_out": DEFAULT_MAILBOX_FORCE_TLS_OUT,
            "tags": DEFAULT_MAILBOX_TAGS
        }
        try:
            return self._get_instance().add('mailbox', data)
        except Exception as e:
            raise MailcowApiException(e)

    def get_all_mailboxes(self) -> object:
        return self._get_instance().get('mailbox', 'all')

    def get_mailboxes(self, username: str = '') -> object:
        try:
            if username == '':
                username = 'all'
            return self._get_instance().get('mailbox', username)
        except Exception as e:
            raise MailcowApiException(e)
