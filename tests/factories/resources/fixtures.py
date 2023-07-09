import pytest

from .person import PersonComputersRelationship, PersonDetail, PersonList


@pytest.fixture()
def person_list():
    yield PersonList


@pytest.fixture()
def person_detail():
    yield PersonDetail


@pytest.fixture()
def person_computers():
    yield PersonComputersRelationship
