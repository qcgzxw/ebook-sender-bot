from peewee import *

database_proxy = DatabaseProxy()


class BaseModel(Model):
    def __del__(self):
        database_proxy.close()

    class Meta:
        database = database_proxy

