import datetime
import json

from peewee import *

from app.model.base import BaseModel

MESSAGE_TYPE_COMMAND = 'command'
MESSAGE_TYPE_TEXT = 'text'
MESSAGE_TYPE_DOCUMENT = 'document'
MESSAGE_TYPE_OTHER = 'other'

FORWARD_TYPE_BOT = 'bot'
FORWARD_TYPE_USER = 'user'
# Set when the original sender hid their account: only a display name survives, no id.
FORWARD_TYPE_HIDDEN = 'hidden'


class UserMessageLog(BaseModel):
    # telegram_id is stored raw instead of as a ForeignKey to User on purpose: this table is
    # written from a group=-1 handler that runs before any handler builds the User row, so a
    # brand new user's first message would have nothing to point at.
    telegram_id = CharField(default='', max_length=20, index=True)
    chat_id = CharField(default='', max_length=20)
    message_id = CharField(default='', max_length=20)
    username = CharField(default='', max_length=128)
    message_type = CharField(default=MESSAGE_TYPE_OTHER, max_length=20, index=True)
    command = CharField(default='', max_length=64)
    text = TextField(default='')
    file_name = CharField(default='', max_length=255)
    file_unique_id = CharField(default='', max_length=200)
    file_size = BigIntegerField(default=0)
    mime_type = CharField(default='', max_length=100)
    # Forward provenance. All four stay empty for messages the user sent themselves.
    forward_from_id = CharField(default='', max_length=20, index=True)
    forward_from_type = CharField(default='', max_length=20)
    # 191, not 255: an indexed utf8mb4 column has to fit MySQL's 767-byte key prefix on older
    # InnoDB row formats. Telegram caps usernames at 32 and chat titles at 128, so nothing is lost.
    forward_from_name = CharField(default='', max_length=191, index=True)
    forward_date = DateTimeField(null=True)
    raw = TextField(default='')
    create_time = DateTimeField(default=datetime.datetime.now, index=True)

    @classmethod
    def log_update(cls, update):
        """Persist one inbound update. Called for every update, before any command handler."""
        row = {'raw': cls._dump_update(update)}
        row.update(cls._parse_user(update.effective_user))
        row.update(cls._parse_message(update.effective_message))
        row.update(cls._parse_forward(update.effective_message))
        chat = update.effective_chat
        if chat is not None:
            row['chat_id'] = str(chat.id)
        # insert() rather than create(): BaseModel.__del__ closes the shared database proxy, so
        # building a model instance for every single update would churn the connection.
        return cls.insert(**row).execute()

    @staticmethod
    def _dump_update(update) -> str:
        # default=str because to_dict() leaves datetime objects in place, which json rejects.
        try:
            return json.dumps(update.to_dict(), ensure_ascii=False, default=str)
        except Exception:
            # A row with only the structured columns still beats no row at all.
            return ''

    @staticmethod
    def _display_name(user) -> str:
        """Prefer @username, fall back to the first/last name pair, mirroring User.find_or_create."""
        first_name = "" if user.first_name is None else user.first_name
        last_name = "" if user.last_name is None else user.last_name
        nickname = " ".join((first_name, last_name)).strip()
        return nickname if user.username is None else user.username

    @classmethod
    def _parse_user(cls, user) -> dict:
        if user is None:
            return {}
        return {
            'telegram_id': str(user.id),
            'username': cls._display_name(user),
        }

    @classmethod
    def _parse_forward(cls, message) -> dict:
        """Record where a forwarded message originally came from."""
        if message is None or message.forward_date is None:
            return {}

        # forward_date arrives tz-aware UTC while create_time is naive local; storing both
        # unchanged would make the two columns incomparable. Full UTC value stays in raw.
        row = {'forward_date': message.forward_date.astimezone().replace(tzinfo=None)}

        origin_user = message.forward_from
        origin_chat = message.forward_from_chat
        if origin_user is not None:
            row['forward_from_id'] = str(origin_user.id)
            row['forward_from_type'] = FORWARD_TYPE_BOT if origin_user.is_bot else FORWARD_TYPE_USER
            row['forward_from_name'] = cls._display_name(origin_user)[:191]
        elif origin_chat is not None:
            row['forward_from_id'] = str(origin_chat.id)
            # 'channel', 'group' or 'supergroup'
            row['forward_from_type'] = origin_chat.type or ''
            row['forward_from_name'] = (origin_chat.username or origin_chat.title or '')[:191]
        elif message.forward_sender_name:
            row['forward_from_type'] = FORWARD_TYPE_HIDDEN
            row['forward_from_name'] = message.forward_sender_name[:191]
        return row

    @staticmethod
    def _parse_message(message) -> dict:
        # effective_message is None for updates that carry no message at all (callback queries,
        # poll answers). Those still get a row, carrying just raw.
        if message is None:
            return {}

        row = {'message_id': str(message.message_id)}
        document = message.document
        if document is not None:
            row['message_type'] = MESSAGE_TYPE_DOCUMENT
            row['file_name'] = document.file_name or ''
            row['file_unique_id'] = document.file_unique_id or ''
            row['file_size'] = document.file_size or 0
            row['mime_type'] = document.mime_type or ''
            row['text'] = message.caption or ''
            return row

        text = message.text or ''
        row['text'] = text
        if text.startswith('/'):
            row['message_type'] = MESSAGE_TYPE_COMMAND
            # "/email@some_bot foo@kindle.com" -> "/email"
            row['command'] = text.split()[0].split('@')[0][:64]
        elif text:
            row['message_type'] = MESSAGE_TYPE_TEXT
        return row
