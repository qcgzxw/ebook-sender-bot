import datetime
import os

from peewee import *

database_proxy = DatabaseProxy()


class BaseModel(Model):
    def __del__(self):
        database_proxy.close()

    class Meta:
        database = database_proxy


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
                .where((UserSendLog.send_time >= datetime.date.today()) & (User.id == self.id))
                .count()
                )

    def log_send_email(self):
        return (
            UserSendLog.create(user=self)
        )

    def is_developer(self):
        return os.getenv('TELEGRAM_DEVELOP_CHAT_ID', '') == self.telegram_id


class UserEmail(BaseModel):
    # todo: kindle_email, file_unique_id
    user = ForeignKeyField(User, backref='emails')
    email = CharField(max_length=100)


class UserSendLog(BaseModel):
    # todo: add columns: email file_unique_id
    user = ForeignKeyField(User, backref='user_send_logs')
    send_time = DateTimeField(default=datetime.datetime.now)
