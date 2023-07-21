import pytest

from .computer import Computer, ComputerSchema
from .person import Person, PersonSchema
from .person_single_tag import PersonSingleTagSchema
from .person_tag import PersonTagSchema


@pytest.fixture()
def person(db):
    person_ = Person(name="test")
    db.session.add(person_)
    db.session.commit()
    yield person_
    db.session.delete(person_)
    db.session.commit()


@pytest.fixture()
def person_2(db):
    person_ = Person(name="test2")
    db.session.add(person_)
    db.session.commit()
    yield person_
    db.session.delete(person_)
    db.session.commit()


@pytest.fixture()
def person_schema():
    return PersonSchema


@pytest.fixture()
def computer(db):
    computer_ = Computer(serial="1")
    db.session.add(computer_)
    db.session.commit()
    yield computer_
    db.session.delete(computer_)
    db.session.commit()


@pytest.fixture()
def computer_schema():
    return ComputerSchema


@pytest.fixture()
def person_tag_schema():
    return PersonTagSchema


@pytest.fixture()
def person_single_tag_schema():
    return PersonSingleTagSchema


@pytest.fixture()
def person_model():
    yield Person
