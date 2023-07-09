from urllib.parse import parse_qs

import pytest

from flask_rest_jsonapi_next.exceptions import BadRequest, InvalidInclude, InvalidSort
from flask_rest_jsonapi_next.pagination import add_pagination_links
from flask_rest_jsonapi_next.querystring import QueryStringManager as QSManager
from flask_rest_jsonapi_next.schema import compute_schema


def test_qs_manager():
    with pytest.raises(ValueError):
        QSManager([], None)


def test_add_pagination_links(app):
    with app.app_context():
        qs = {"page[number]": "2", "page[size]": "10"}
        qsm = QSManager(qs, None)
        pagination_dict = dict()
        add_pagination_links(pagination_dict, 43, qsm, str())
        last_page_dict = parse_qs(pagination_dict["links"]["last"][1:])
        assert len(last_page_dict["page[number]"]) == 1
        assert last_page_dict["page[number]"][0] == "5"


def test_query_string_manager(person_schema):
    query_string = {"page[slumber]": "3"}
    qsm = QSManager(query_string, person_schema)
    with pytest.raises(BadRequest):
        qsm.pagination
    qsm.qs["sort"] = "computers"
    with pytest.raises(InvalidSort):
        qsm.sorting


def test_compute_schema(person_schema):
    query_string = {"page[number]": "3", "fields[person]": list()}
    qsm = QSManager(query_string, person_schema)
    with pytest.raises(InvalidInclude):
        compute_schema(person_schema, dict(), qsm, ["id"])
    compute_schema(person_schema, dict(only=list()), qsm, list())


def test_compute_schema_propagate_context(person_schema, computer_schema):
    query_string = {}
    qsm = QSManager(query_string, person_schema)
    schema = compute_schema(person_schema, dict(), qsm, ["computers"])
    assert (
        schema.declared_fields["computers"]
        .__dict__["_Relationship__schema"]
        .__dict__["context"]
        == dict()
    )
    schema = compute_schema(
        person_schema, dict(context=dict(foo="bar")), qsm, ["computers"]
    )
    assert schema.declared_fields["computers"].__dict__[
        "_Relationship__schema"
    ].__dict__["context"] == dict(foo="bar")
