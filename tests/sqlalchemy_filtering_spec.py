import pytest

from flask_rest_jsonapi_next.data_layers.filtering.alchemy import Node
from flask_rest_jsonapi_next.exceptions import InvalidFilters
from tests.factories.models import Computer
from tests.factories.models.string_json_attribute_person import (
    StringJsonAttributePerson,
    StringJsonAttributePersonSchema,
)


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


def _sql(clause):
    return str(clause.compile(compile_kwargs={"literal_binds": True})).replace(
        "\n", " "
    )


def test_Node_dotted_name_to_many_relationship(person_model, person_schema):
    # "computers.serial" is the dot-notation shortcut for the nested "any" filter.
    filt = {"name": "computers.serial", "op": "ilike", "val": "%Amstrad%"}
    dotted = _sql(Node(person_model, filt, None, person_schema).resolve())

    nested = _sql(
        Node(
            person_model,
            {
                "name": "computers",
                "op": "any",
                "val": {"name": "serial", "op": "ilike", "val": "%Amstrad%"},
            },
            None,
            person_schema,
        ).resolve()
    )

    assert dotted == nested
    assert "EXISTS" in dotted


def test_Node_dotted_name_to_one_relationship(computer_schema):
    # "owner" is mapped onto Computer.person via the field's attribute, and it is a
    # to-one relationship, so it must resolve through "has", not "any".
    filt = {"name": "owner.name", "op": "eq", "val": "John"}
    dotted = _sql(Node(Computer, filt, None, computer_schema).resolve())

    nested = _sql(
        Node(
            Computer,
            {
                "name": "owner",
                "op": "has",
                "val": {"name": "name", "op": "eq", "val": "John"},
            },
            None,
            computer_schema,
        ).resolve()
    )

    assert dotted == nested
    assert "EXISTS" in dotted
    assert "person.name" in dotted


def test_Node_dotted_name_multiple_hops(person_model, person_schema):
    filt = {"name": "computers.owner.name", "op": "eq", "val": "John"}
    resolved = _sql(Node(person_model, filt, None, person_schema).resolve())

    assert resolved.count("EXISTS") == 2
    assert "person.name" in resolved


def test_Node_dotted_name_coerces_leaf_value_by_column_type(
    person_model, person_schema
):
    # Coercion must happen against the *related* model's column, not the relationship.
    filt = {"name": "computers.id", "op": "eq", "val": "42"}
    resolved = _sql(Node(person_model, filt, None, person_schema).resolve())

    assert "computer.id = 42" in resolved


def test_Node_dotted_name_inside_logical_operator(person_model, person_schema):
    filt = {
        "or": [
            {"name": "computers.serial", "op": "ilike", "val": "%Amstrad%"},
            {"name": "name", "op": "eq", "val": "John"},
        ]
    }
    resolved = _sql(Node(person_model, filt, None, person_schema).resolve())

    assert "EXISTS" in resolved
    assert "person.name = 'John'" in resolved


def test_Node_dotted_name_over_nested_field(person_model, person_schema):
    # Person.tags is a marshmallow Nested field backed by a relationship.
    filt = {"name": "tags.key", "op": "eq", "val": "foo"}
    resolved = _sql(Node(person_model, filt, None, person_schema).resolve())

    assert "EXISTS" in resolved
    assert "person_tag.key = 'foo'" in resolved


@pytest.mark.parametrize(
    "name",
    [
        # unknown relationship
        "unknown.serial",
        # known attribute, but not a relationship
        "name.serial",
        # known relationship, unknown attribute on the related schema
        "computers.unknown",
    ],
)
def test_Node_dotted_name_invalid_paths(person_model, person_schema, name):
    filt = {"name": name, "op": "eq", "val": "foo"}

    with pytest.raises(InvalidFilters):
        Node(person_model, filt, None, person_schema).resolve()


def test_Node_double_underscore_name_with_leaf_operator(person_model, person_schema):
    # The legacy "__" shortcut with a leaf operator must behave like dot notation
    # instead of blowing up with a TypeError from SQLAlchemy.
    filt = {"name": "computers__serial", "op": "ilike", "val": "%Amstrad%"}
    resolved = _sql(Node(person_model, filt, None, person_schema).resolve())

    assert "EXISTS" in resolved
    assert "computer.serial" in resolved


def test_Node_double_underscore_name_with_has_operator(computer_schema):
    # The kwargs form of "has"/"any" keeps working.
    filt = {"name": "owner__name", "op": "has", "val": "John"}
    resolved = _sql(Node(Computer, filt, None, computer_schema).resolve())

    assert "EXISTS" in resolved
    assert "person.name = 'John'" in resolved


def test_Node_double_underscore_name_over_non_relationship(person_model, person_schema):
    # A "__" in a name that isn't a relationship traversal is a bad request, not a
    # TypeError bubbling out of SQLAlchemy.
    filt = {"name": "name__foo", "op": "eq", "val": "John"}

    with pytest.raises(InvalidFilters):
        Node(person_model, filt, None, person_schema).resolve()


def test_Node_dotted_name_over_json_backed_nested_field():
    # StringJsonAttributePerson.address is a Nested field mapped onto a JSON column:
    # it is a nested field, but there is nothing to traverse into.
    filt = {"name": "address.city", "op": "eq", "val": "Raleigh"}

    with pytest.raises(InvalidFilters):
        Node(
            StringJsonAttributePerson,
            filt,
            None,
            StringJsonAttributePersonSchema,
        ).resolve()
