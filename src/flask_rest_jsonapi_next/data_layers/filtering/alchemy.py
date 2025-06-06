"""Helper to create sqlalchemy filters according to filter querystring parameter"""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, Mapping, Union

from dateutil import parser
from sqlalchemy import and_, not_, or_

from ...exceptions import InvalidFilters
from ...schema import get_model_field, get_nested_fields, get_relationships


def create_filters(model, filter_info, resource):
    """Apply filters from filters information to base query

    :param DeclarativeMeta model: the model of the node
    :param dict filter_info: current node filter information
    :param Resource resource: the resource
    """
    filters = []

    for filter_ in filter_info:
        resolved = Node(model, filter_, resource, resource.schema).resolve()
        if resolved is not None:
            filters.append(resolved)

    return filters


class Node(object):
    """Helper to recursively create filters with sqlalchemy according to filter querystring parameter"""

    def __init__(self, model, filter_, resource, schema):
        """Initialize an instance of a filter node

        :param Model model: an sqlalchemy model
        :param dict filter_: filters information of the current node and deeper nodes
        :param Resource resource: the base resource to apply filters on
        :param Schema schema: the serializer of the resource
        """
        self.model = model
        self.filter_ = filter_
        self.resource = resource
        self.schema = schema

    def resolve(self):
        """Create filter for a particular node of the filter tree"""
        if (
            "or" not in self.filter_
            and "and" not in self.filter_
            and "not" not in self.filter_
        ):
            value = self.value

            if self.operator == "between":
                return self.column.between(*value)

            if isinstance(value, dict):
                value = Node(
                    self.related_model, value, self.resource, self.related_schema
                ).resolve()

            if "__" in self.filter_.get("name", ""):
                value = {self.filter_["name"].split("__")[1]: value}

            if isinstance(value, dict):
                return getattr(self.column, self.operator)(
                    **{k: v for k, v in value.items()}
                )
            else:
                return getattr(self.column, self.operator)(value)

        if "or" in self.filter_ and self.filter_["or"]:
            return or_(
                Node(self.model, filt, self.resource, self.schema).resolve()
                for filt in self.filter_["or"]
            )
        if "and" in self.filter_ and self.filter_["and"]:
            return and_(
                Node(self.model, filt, self.resource, self.schema).resolve()
                for filt in self.filter_["and"]
            )
        if "not" in self.filter_ and self.filter_["not"]:
            return not_(
                Node(
                    self.model, self.filter_["not"], self.resource, self.schema
                ).resolve()
            )

    @property
    def name(self):
        """Return the name of the node or raise a BadRequest exception

        :return str: the name of the field to filter on
        """
        name = self.filter_.get("name")

        if name is None:
            raise InvalidFilters("Can't find name of a filter")

        if "__" in name:
            name = name.split("__")[0]

        if name not in self.schema._declared_fields:
            raise InvalidFilters(
                "{} has no attribute {}".format(self.schema.__name__, name)
            )

        return name

    @property
    def op(self):
        """Return the operator of the node

        :return str: the operator to use in the filter
        """
        try:
            return self.filter_["op"]
        except KeyError:
            raise InvalidFilters("Can't find op of a filter")

    @property
    def column(self):
        """Get the column object

        :param DeclarativeMeta model: the model
        :param str field: the field
        :return InstrumentedAttribute: the column to filter on
        """
        field = self.name

        model_field = get_model_field(self.schema, field)

        try:
            return getattr(self.model, model_field)
        except AttributeError:
            raise InvalidFilters(
                "{} has no attribute {}".format(self.model.__name__, model_field)
            )

    @property
    def operator(self):
        """Get the function operator from his name

        :return callable: a callable to make operation on a column
        """
        operators = (self.op, self.op + "_", "__" + self.op + "__")

        for op in operators:
            if hasattr(self.column, op):
                return op

        raise InvalidFilters("{} has no operator {}".format(self.column.key, self.op))

    @property
    def value(self):
        """Get the value to filter on

        :return: the value to filter on
        """
        if self.filter_.get("field") is not None:
            try:
                result = getattr(self.model, self.filter_["field"])
            except AttributeError:
                raise InvalidFilters(
                    "{} has no attribute {}".format(
                        self.model.__name__, self.filter_["field"]
                    )
                )
            else:
                return result
        else:
            if "val" not in self.filter_:
                raise InvalidFilters("Can't find value or field in a filter")

            return self._coerce(self.filter_["val"])

    @classmethod
    def _coerce(
        cls, value: Union[Mapping, Iterable, str, int, float]
    ) -> Union[str, int, float, date, datetime, list, dict, Decimal]:
        if isinstance(value, str):
            try:
                return int(value)
            except Exception:
                pass

            try:
                return parser.isoparse(value)
            except Exception:
                pass

            try:
                return Decimal(value)
            except Exception:
                pass

            return value

        elif isinstance(value, Mapping):
            return {k: cls._coerce(v) for k, v in value.items()}

        elif isinstance(value, Iterable):
            return [cls._coerce(_) for _ in value]

        else:
            return value

    @property
    def related_model(self):
        """Get the related model of a related (relationship or nested) field

        :return DeclarativeMeta: the related model
        """
        related_field_name = self.name

        related_fields = get_relationships(self.schema) + get_nested_fields(self.schema)
        if related_field_name not in related_fields:
            raise InvalidFilters(
                "{} has no relationship or nested attribute {}".format(
                    self.schema.__name__, related_field_name
                )
            )

        return getattr(
            self.model, get_model_field(self.schema, related_field_name)
        ).property.mapper.class_

    @property
    def related_schema(self):
        """Get the related schema of a related (relationship or nested) field

        :return Schema: the related schema
        """
        related_field_name = self.name
        related_fields = get_relationships(self.schema) + get_nested_fields(self.schema)
        if related_field_name not in related_fields:
            raise InvalidFilters(
                "{} has no relationship or nested attribute {}".format(
                    self.schema.__name__, related_field_name
                )
            )

        return self.schema._declared_fields[related_field_name].schema.__class__
