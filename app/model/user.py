import datetime

from peewee import *

from app.config.configs import telegram_config, provider_config
from app.model.base import BaseModel
from app.utils.util import gen_sender_email_username, gen_sender_email_password


class User(BaseModel):
    telegram_id = CharField(unique=True, max_length=20)
    username = CharField(max_length=128)
    nickname = CharField(default=None, max_length=250)
    is_vip = BooleanField(default=False)
    join_time = DateTimeField(default=datetime.datetime.now)

    @staticmethod
    def find_or_create(from_user):
        telegram_id = str(from_user.id)
        first_name = "" if from_user.first_name is None else from_user.first_name
        last_name = "" if from_user.last_name is None else from_user.last_name
        nickname = " ".join((first_name, last_name))
        username = nickname if from_user.username is None else from_user.username
        user, _ = User.get_or_create(telegram_id=telegram_id,
                                     defaults={'username': username,
                                               'nickname': nickname})
        if username != user.username or nickname != user.nickname:
            user.username = username
            user.nickname = nickname
            user.save()
        return user

    def set_email_sender(self):
        if len(self.emails) == 0:
            return UserEmail.create(
                user=self,
                email="",
                sender_email=gen_sender_email_username(self.telegram_id),
                sender_email_password=gen_sender_email_password(),
                sender_email_created=0
            )
        else:
            # todo: one2many update bug
            if self.emails[0].sender_email is None or self.emails[0].sender_email == "":
                return UserEmail.update(
                    sender_email=gen_sender_email_username(self.telegram_id),
                    sender_email_password=gen_sender_email_password()
                ).where(UserEmail.user == self).execute()

    def set_email(self, email: str):
        if len(self.emails) == 0:
            return UserEmail.create(user=self, email=email)
        else:
            # todo: one2many update bug
            return UserEmail.update(email=email).where(UserEmail.user == self).execute()

    def today_send_times(self):
        return (User
                .select()
                .join(UserSendLog)
                .where(
                    (UserSendLog.send_time >= datetime.date.today())
                    & (User.id == self.id)
                    & (UserSendLog.status == 1)
                )
                .count()
                )

    def log_send_email(self, sender_email: str, file_unique_id: str):
        return (
            UserSendLog.create(user=self, email=self.emails[0].email, sender_email=sender_email, file_unique_id=file_unique_id)
        )

    def log_created_email(self):
        return UserEmail.update(sender_email_created=1).where(UserEmail.user == self).execute()

    def is_developer(self):
        return telegram_config('developer_chat_id') == self.telegram_id


class UserEmail(BaseModel):
    user = ForeignKeyField(User, backref='emails')
    email = CharField(max_length=100)
    sender_email = CharField(default=None, max_length=200)
    sender_email_password = CharField(default=None, max_length=200)
    sender_email_created = SmallIntegerField(default=0)


class UserSendLog(BaseModel):
    user = ForeignKeyField(User, backref='user_send_logs')
    email = CharField(max_length=100)
    sender_email = CharField(max_length=200)
    file_unique_id = CharField(max_length=200)
    status = SmallIntegerField(default=0)
    send_time = DateTimeField(default=datetime.datetime.now)

    def send_succeed(self):
        self.status = 1
        return self.save()

    def send_failed(self):
        self.status = 2
        return self.save()


def get_send_history(start_time=None):
    query = UserSendLog.select(User.username, User.telegram_id, fn.COUNT(UserSendLog.id).alias('num_logs'))
    if start_time:
        query = query.where(UserSendLog.send_time >= start_time)
    return query.join(User).group_by(User.telegram_id).order_by(fn.COUNT(UserSendLog.id).desc()).dicts()
