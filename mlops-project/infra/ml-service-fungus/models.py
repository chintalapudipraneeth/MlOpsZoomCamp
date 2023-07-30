import os
import datetime

from peewee import (
    Model,
    CharField,
    BooleanField,
    DateTimeField,
    ForeignKeyField,
    PostgresqlDatabase,
)

psql_db = PostgresqlDatabase(
    os.getenv('DB'),
    user=os.getenv('USER_DB'),
    password=os.getenv('PASSWORD_DB'),
    host=os.getenv('HOST_DB'),
)


class BaseModel(Model):
    """A base model that will use our Postgresql database"""

    class Meta:
        database = psql_db


class Field(BaseModel):
    field = CharField(unique=True)
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(null=True)


class Value(BaseModel):
    value = CharField()
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(null=True)

    field_id = ForeignKeyField(Field)

    class Meta:
        indexes = ((('value', 'field_id'), True),)
