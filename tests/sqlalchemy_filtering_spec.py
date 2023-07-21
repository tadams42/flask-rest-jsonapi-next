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
