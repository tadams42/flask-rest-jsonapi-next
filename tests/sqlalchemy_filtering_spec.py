import pytest

from flask_rest_jsonapi_next.data_layers.filtering.alchemy import Node
from flask_rest_jsonapi_next.exceptions import InvalidFilters


def test_Node(person_model, person_schema):
    from copy import deepcopy

    filt = {
        "val": "0000",
        "field": True,
        "not": dict(),
        "name": "name",
        "op": "eq",
        "strip": lambda: "s",
    }
    filt["not"] = deepcopy(filt)
    del filt["not"]["not"]
    n = Node(person_model, filt, None, person_schema)
    with pytest.raises(TypeError):
        # print(n.val is None and n.field is None)
        # # n.column
        n.resolve()
    with pytest.raises(AttributeError):
        n.model = None
        n.column
    with pytest.raises(InvalidFilters):
        n.model = person_model
        n.filter_["op"] = ""
        n.operator
    with pytest.raises(InvalidFilters):
        n.related_model
    with pytest.raises(InvalidFilters):
        n.related_schema


def test_Node_empty_filter(person_model, person_schema):
    for filt in [
        {"and": []},
        {"or": []},
        {"not": []},
    ]:
        resolved = Node(person_model, filt, None, person_schema).resolve()
        assert resolved is None


def test_Node_or_with_empty_sub_filter_drops_empty_clause(person_model, person_schema):
    # {"and": []} inside an "or" resolves to None — it must be dropped rather than
    # passed as None to SQLAlchemy's or_(), which would be undefined behavior.
    filt = {
        "or": [
            {"and": []},
            {"name": "name", "op": "eq", "val": "foo"},
        ]
    }
    resolved = Node(person_model, filt, None, person_schema).resolve()
    assert resolved is not None


def test_Node_and_with_empty_sub_filter_drops_empty_clause(person_model, person_schema):
    filt = {
        "and": [
            {"or": []},
            {"name": "name", "op": "eq", "val": "foo"},
        ]
    }
    resolved = Node(person_model, filt, None, person_schema).resolve()
    assert resolved is not None


def test_Node_or_all_empty_sub_filters_returns_none(person_model, person_schema):
    # All sub-filters are empty — result should be None (no filter applied),
    # consistent with the top-level empty or/and behaviour.
    filt = {"or": [{"and": []}, {"or": []}]}
    resolved = Node(person_model, filt, None, person_schema).resolve()
    assert resolved is None


def test_Node_not_with_empty_inner_filter_returns_none(person_model, person_schema):
    # not_() wrapping None (from an empty inner filter) must not be passed to
    # SQLAlchemy — it should return None instead.
    filt = {"not": {"and": []}}
    resolved = Node(person_model, filt, None, person_schema).resolve()
    assert resolved is None
