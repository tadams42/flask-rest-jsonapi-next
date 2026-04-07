import pytest
import sqlalchemy

from flask_rest_jsonapi_next import JsonApiException, SqlalchemyDataLayer
from flask_rest_jsonapi_next.data_layers.base import BaseDataLayer
from flask_rest_jsonapi_next.exceptions import InvalidSort, RelationNotFound
from tests.factories.models import Computer


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
        dl.sort_query(None, [dict(field="test", order="asc")])


def test_sqlalchemy_data_layer_sort_query_simple_asc(db, person_model, monkeypatch):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    query = db.session.query(person_model)
    dl.sort_query(query, [dict(field="name", order="asc")])


def test_sqlalchemy_data_layer_sort_query_relation(db, person_model, monkeypatch):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    query = db.session.query(person_model)
    dl.sort_query(query, [dict(field="single_tag.key", order="asc")])


def test_sqlalchemy_data_layer_sort_query_relation_multiple(
    db, person_model, monkeypatch
):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    query = db.session.query(person_model)
    dl.sort_query(
        query,
        [
            dict(field="single_tag.key", order="asc"),
            dict(field="single_tag.value", order="asc"),
            dict(field="computers.serial", order="asc"),
        ],
    )


def test_sqlalchemy_data_layer_sort_query_simple_relation_error(
    db, person_model, monkeypatch
):
    with pytest.raises(InvalidSort):
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        query = db.session.query(person_model)
        dl.sort_query(
            query, [dict(field="single_tag.non_existent_property", order="asc")]
        )


# ---------------------------------------------------------------------------
# Relationship operations: data-manipulation with integer PKs
#
# create_relationship and delete_relationship convert existing PKs to str()
# before comparing against the JSON string ID from the request.  Without
# that conversion, int(1) != str("1"), so:
#   - create_relationship would always add duplicates
#   - delete_relationship would never match and remove items
# update_relationship compares model integers against model integers (both
# sides come from loaded ORM objects), so no str() conversion is needed
# there — but the set-equality semantics still need exercising.
# ---------------------------------------------------------------------------


def test_create_relationship_to_many_adds_related_object(
    db, person_model, person, computer
):
    """A computer not yet linked to a person is added, and updated=True is returned."""
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    json_data = {"data": [{"type": "computer", "id": str(computer.id)}]}

    obj, updated = dl.create_relationship(
        json_data, "computers", "id", {"id": person.person_id}
    )

    db.session.refresh(person)
    assert updated is True
    assert computer in person.computers


def test_create_relationship_to_many_is_idempotent_with_integer_pk(
    db, person_model, person, computer
):
    """POSTing a computer that is already linked must not create a duplicate.

    The guard compares str(existing_pk) against the JSON string ID.  If the
    str() conversion were missing, int(1) != str("1") and every POST would
    append a duplicate regardless of whether the link already exists.
    """
    person.computers.append(computer)
    db.session.commit()
    db.session.expire_all()

    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    json_data = {"data": [{"type": "computer", "id": str(computer.id)}]}

    obj, updated = dl.create_relationship(
        json_data, "computers", "id", {"id": person.person_id}
    )

    db.session.refresh(person)
    assert updated is False
    assert len(person.computers) == 1


def test_delete_relationship_to_many_removes_related_object(
    db, person_model, person, computer
):
    """A computer that is linked to a person is removed, and updated=True is returned."""
    person.computers.append(computer)
    db.session.commit()
    db.session.expire_all()

    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    json_data = {"data": [{"type": "computer", "id": str(computer.id)}]}

    obj, updated = dl.delete_relationship(
        json_data, "computers", "id", {"id": person.person_id}
    )

    db.session.refresh(person)
    assert updated is True
    assert computer not in person.computers


def test_delete_relationship_to_many_skips_unlinked_object_with_integer_pk(
    db, person_model, person, computer
):
    """DELETEing a computer that is NOT in the person's list must be a no-op.

    The guard checks str(existing_pk) against the JSON string ID.  If the
    str() conversion were missing, the in-set check would always be False
    for integer PKs, silently swallowing removal requests that should work.
    The inverse risk tested here: a non-member must not accidentally match.
    """
    # Create a second computer and link only that one to the person so the
    # person's computer list is non-empty but does not contain `computer`.
    other = Computer(serial="other")
    db.session.add(other)
    person.computers.append(other)
    db.session.commit()
    db.session.expire_all()

    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    json_data = {"data": [{"type": "computer", "id": str(computer.id)}]}

    obj, updated = dl.delete_relationship(
        json_data, "computers", "id", {"id": person.person_id}
    )

    db.session.refresh(person)
    assert updated is False
    assert other in person.computers

    # clean up the extra computer
    db.session.delete(other)
    db.session.commit()


def test_update_relationship_to_many_replaces_set(db, person_model, person, computer):
    """PATCH replaces the full relationship set; the new computer must appear."""
    other = Computer(serial="replacement")
    db.session.add(other)
    person.computers.append(computer)
    db.session.commit()
    db.session.expire_all()

    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    json_data = {"data": [{"type": "computer", "id": str(other.id)}]}

    obj, updated = dl.update_relationship(
        json_data, "computers", "id", {"id": person.person_id}
    )

    db.session.refresh(person)
    assert updated is True
    assert other in person.computers
    assert computer not in person.computers

    db.session.delete(other)
    db.session.commit()


def test_update_relationship_to_many_no_op_when_set_unchanged(
    db, person_model, person, computer
):
    """PATCHing with the same set of IDs returns updated=False and changes nothing."""
    person.computers.append(computer)
    db.session.commit()
    db.session.expire_all()

    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    json_data = {"data": [{"type": "computer", "id": str(computer.id)}]}

    obj, updated = dl.update_relationship(
        json_data, "computers", "id", {"id": person.person_id}
    )

    db.session.refresh(person)
    assert updated is False
    assert person.computers == [computer]


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
