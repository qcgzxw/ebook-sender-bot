import datetime

from peewee import *

from app.config.configs import telegram_config
from app.model.base import BaseModel


class User(BaseModel):
    telegram_id = CharField(unique=True, max_length=20)
    username = CharField(max_length=128)
    nickname = CharField(default=None, max_length=250)
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

    def log_send_email(self, file_unique_id: str):
        return (
            UserSendLog.create(user=self, email=self.emails[0].email, file_unique_id=file_unique_id)
        )

    def is_developer(self):
        return telegram_config('developer_chat_id') == self.telegram_id


class UserEmail(BaseModel):
    user = ForeignKeyField(User, backref='emails')
    email = CharField(max_length=100)


class UserSendLog(BaseModel):
    user = ForeignKeyField(User, backref='user_send_logs')
    email = CharField(max_length=100)
    file_unique_id = CharField(max_length=200)
    status = SmallIntegerField(default=0)
    send_time = DateTimeField(default=datetime.datetime.now)

    def send_succeed(self):
        self.status = 1
        return self.save()

    def send_failed(self):
        self.status = 2
        return self.save()
