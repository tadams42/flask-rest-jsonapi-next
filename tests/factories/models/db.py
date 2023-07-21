import json

import pytest
import sqlalchemy.types as types
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class StringyJSON(types.TypeDecorator):
    """
    Stores and retrieves JSON as TEXT.

    This approach to faking JSON support for testing with sqlite is borrowed from:
    https://avacariu.me/articles/2016/compiling-json-as-text-for-sqlite-with-sqlalchemy
    """

    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


# TypeEngine.with_variant says "use StringyJSON instead when connecting to 'sqlite'"
MagicJSON = types.JSON().with_variant(StringyJSON, "sqlite")


class Db:
    def __init__(self) -> None:
        self.engine = create_engine("sqlite:///:memory:")
        self.Session = sessionmaker(bind=self.engine)
        self._session = scoped_session(session_factory=self.Session)
        self._upgraded = False

    @property
    def session(self):
        if not self._upgraded:
            self._upgrade()
        return self._session

    def _upgrade(self):
        from .computer import Computer
        from .person import Person
        from .person_single_tag import PersonSingleTag
        from .person_tag import PersonTag
        from .string_json_attribute_person import StringJsonAttributePerson

        PersonTag.metadata.create_all(self.engine)
        PersonSingleTag.metadata.create_all(self.engine)
        Person.metadata.create_all(self.engine)
        Computer.metadata.create_all(self.engine)
        StringJsonAttributePerson.metadata.create_all(self.engine)

        self._upgraded = True


# Usually in Flask we have one global proxy object that is used anywhere in app.
# For purpose of our tests, we simulate that situation with following constant:
APP_DB = Db()


@pytest.fixture(scope="session")
def db():
    yield APP_DB
