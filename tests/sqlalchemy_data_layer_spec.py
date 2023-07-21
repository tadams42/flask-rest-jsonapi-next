import pytest
import sqlalchemy

from flask_rest_jsonapi_next import JsonApiException, SqlalchemyDataLayer
from flask_rest_jsonapi_next.data_layers.base import BaseDataLayer
from flask_rest_jsonapi_next.exceptions import InvalidSort, RelationNotFound


def test_sqlalchemy_data_layer_without_session(person_model, person_list):
    with pytest.raises(Exception):
        SqlalchemyDataLayer(dict(model=person_model, resource=person_list))


def test_sqlalchemy_data_layer_without_model(db, person_list):
    with pytest.raises(Exception):
        SqlalchemyDataLayer(dict(session=db.session, resource=person_list))


def test_sqlalchemy_data_layer_create_object_error(db, person_model, person_list):
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        dl = SqlalchemyDataLayer(
            dict(session=db.session, model=person_model, resource=person_list)
        )
        dl.create_object(dict(), dict())


def test_sqlalchemy_data_layer_get_object_error(db, person_model):
    with pytest.raises(Exception):
        dl = SqlalchemyDataLayer(
            dict(session=db.session, model=person_model, id_field="error")
        )
        dl.get_object(dict())


def test_sqlalchemy_data_layer_update_object_error(
    db, person_model, person_list, monkeypatch
):
    def commit_mock():
        raise JsonApiException()

    with pytest.raises(JsonApiException):
        dl = SqlalchemyDataLayer(
            dict(session=db.session, model=person_model, resource=person_list)
        )
        monkeypatch.setattr(dl.session, "commit", commit_mock)
        dl.update_object(dict(), dict(), dict())


def test_sqlalchemy_data_layer_delete_object_error(
    db, person_model, person_list, monkeypatch
):
    def commit_mock():
        raise JsonApiException()

    def delete_mock(obj):
        pass

    with pytest.raises(JsonApiException):
        dl = SqlalchemyDataLayer(
            dict(session=db.session, model=person_model, resource=person_list)
        )
        monkeypatch.setattr(dl.session, "commit", commit_mock)
        monkeypatch.setattr(dl.session, "delete", delete_mock)
        dl.delete_object(dict(), dict())


def test_sqlalchemy_data_layer_create_relationship_field_not_found(db, person_model):
    with pytest.raises(Exception):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        dl.create_relationship(dict(), "error", "", dict(id=1))


def test_sqlalchemy_data_layer_create_relationship_error(
    db, person_model, get_object_mock, monkeypatch
):
    def commit_mock():
        raise JsonApiException()

    with pytest.raises(JsonApiException):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        monkeypatch.setattr(dl.session, "commit", commit_mock)
        monkeypatch.setattr(dl, "get_object", get_object_mock)
        dl.create_relationship(dict(data=None), "foo", "", dict(id=1))


def test_sqlalchemy_data_layer_get_relationship_field_not_found(
    db, person_model, person
):
    with pytest.raises(RelationNotFound):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        dl.get_relationship("error", "", "", dict(id=person.person_id))


def test_sqlalchemy_data_layer_update_relationship_field_not_found(db, person_model):
    with pytest.raises(Exception):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        dl.update_relationship(dict(), "error", "", dict(id=1))


def test_sqlalchemy_data_layer_update_relationship_error(
    db, person_model, get_object_mock, monkeypatch
):
    def commit_mock():
        raise JsonApiException()

    with pytest.raises(JsonApiException):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        monkeypatch.setattr(dl.session, "commit", commit_mock)
        monkeypatch.setattr(dl, "get_object", get_object_mock)
        dl.update_relationship(dict(data=None), "foo", "", dict(id=1))


def test_sqlalchemy_data_layer_delete_relationship_field_not_found(db, person_model):
    with pytest.raises(Exception):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        dl.delete_relationship(dict(), "error", "", dict(id=1))


def test_sqlalchemy_data_layer_delete_relationship_error(
    db, person_model, get_object_mock, monkeypatch
):
    def commit_mock():
        raise JsonApiException()

    with pytest.raises(JsonApiException):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        monkeypatch.setattr(dl.session, "commit", commit_mock)
        monkeypatch.setattr(dl, "get_object", get_object_mock)
        dl.delete_relationship(dict(data=None), "foo", "", dict(id=1))


def test_sqlalchemy_data_layer_sort_query_error(db, person_model, monkeypatch):
    with pytest.raises(InvalidSort):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        dl.sort_query(None, [dict(field="test")])


def test_base_data_layer():
    base_dl = BaseDataLayer(dict())
    with pytest.raises(NotImplementedError):
        base_dl.create_object(None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.get_object(dict())
    with pytest.raises(NotImplementedError):
        base_dl.get_collection(None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.update_object(None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.delete_object(None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.create_relationship(None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.get_relationship(None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.update_relationship(None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.delete_relationship(None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.query(dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_create_object(None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_create_object(None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_get_object(dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_get_object(None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_get_collection(None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_get_collection(None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_update_object(None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_update_object(None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_delete_object(None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_delete_object(None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_create_relationship(None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_create_relationship(None, None, None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_get_relationship(None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_get_relationship(None, None, None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_update_relationship(None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_update_relationship(None, None, None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.before_delete_relationship(None, None, None, dict())
    with pytest.raises(NotImplementedError):
        base_dl.after_delete_relationship(None, None, None, None, None, dict())
