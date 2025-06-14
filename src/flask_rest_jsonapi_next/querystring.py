"""Helper to deal with querystring parameters according to jsonapi specification"""

import json

from flask import current_app

from .exceptions import (
    BadRequest,
    InvalidField,
    InvalidFilters,
    InvalidInclude,
    InvalidSort,
)
from .schema import get_model_field, get_relationships, get_schema_from_type


class QueryStringManager(object):
    """Querystring parser according to jsonapi reference"""

    MANAGED_KEYS = ("filter", "page", "fields", "sort", "include", "q")

    def __init__(
        self, querystring, schema, allow_disable_pagination=None, max_page_size=None
    ):
        """Initialization instance

        :param dict querystring: query string dict from request.args
        """
        if not isinstance(querystring, dict):
            raise ValueError(
                "QueryStringManager require a dict-like object querystring parameter"
            )

        self.qs = querystring
        self.schema = schema

        self.allow_disable_pagination = allow_disable_pagination
        self.max_page_size = max_page_size

    def _get_key_values(self, name):
        """Return a dict containing key / values items for a given key, used for items like filters, page, etc.

        :param str name: name of the querystring parameter
        :return dict: a dict of key / values items
        """
        results = {}

        for key, value in self.qs.items():
            try:
                if not key.startswith(name):
                    continue

                key_start = key.index("[") + 1
                key_end = key.index("]")
                item_key = key[key_start:key_end]

                if "," in value:
                    item_value = value.split(",")
                else:
                    item_value = value
                results.update({item_key: item_value})
            except Exception:
                raise BadRequest("Parse error", source={"parameter": key})

        return results

    def _simple_filters(self, dict_):
        """Return filter list

        :return list: list of dict for filter parameters. Includes support for 'in' for list values
        """
        filter_list = []
        for key, value in dict_.items():
            operator = "eq"
            if isinstance(value, list):
                operator = "in"
            filter_list.append({"name": key, "op": operator, "val": value})
        return filter_list

    @property
    def querystring(self):
        """Return original querystring but containing only managed keys

        :return dict: dict of managed querystring parameter
        """
        return {
            key: value
            for (key, value) in self.qs.items()
            if key.startswith(self.MANAGED_KEYS) or self._get_key_values("filter[")
        }

    @property
    def filters(self):
        """Return filters from query string.

        :return list: filter information
        """
        results = []
        filters = self.qs.get("filter")
        if filters is not None:
            try:
                data = json.loads(filters)

                if isinstance(data, dict):
                    results.append(data)
                else:
                    results.extend(data)

            except (ValueError, TypeError):
                raise InvalidFilters("Parse error")

        if self._get_key_values("filter["):
            results.extend(self._simple_filters(self._get_key_values("filter[")))

        return results

    @property
    def pagination(self):
        """Return all page parameters as a dict.

        :return dict: a dict of pagination information

        To allow multiples strategies, all parameters starting with `page` will be included. e.g::

            {
                "number": '25',
                "size": '150',
            }

        Example with number strategy::

            >>> query_string = {'page[number]': '25', 'page[size]': '10'}
            >>> parsed_query.pagination
            {'number': '25', 'size': '10'}
        """
        # check values type
        result = self._get_key_values("page")
        for key, value in result.items():
            if key not in ("number", "size"):
                raise BadRequest(
                    "{} is not a valid parameter of pagination".format(key),
                    source={"parameter": "page"},
                )
            try:
                int(value)
            except ValueError:
                raise BadRequest(
                    "Parse error", source={"parameter": "page[{}]".format(key)}
                )

        if self.allow_disable_pagination is None:
            self.allow_disable_pagination = current_app.config.get(
                "ALLOW_DISABLE_PAGINATION", True
            )

        if self.max_page_size is None:
            self.max_page_size = current_app.config.get("MAX_PAGE_SIZE", None)

        if not self.allow_disable_pagination and int(result.get("size", 1)) == 0:
            raise BadRequest(
                "You are not allowed to disable pagination",
                source={"parameter": "page[size]"},
            )

        if self.max_page_size is not None and "size" in result:
            if int(result["size"]) > self.max_page_size:
                raise BadRequest(
                    f"Maximum page size is {self.max_page_size}",
                    source={"parameter": "page[size]"},
                )

        return result

    @property
    def fields(self):
        """Return fields wanted by client.

        :return dict: a dict of sparse fieldsets information

        Return value will be a dict containing all fields by resource, for example::

            {
                "user": ['name', 'email'],
            }

        """
        result = self._get_key_values("fields")
        for key, value in result.items():
            if not isinstance(value, list):
                result[key] = [value]

        for key, value in result.items():
            schema = get_schema_from_type(key)
            for obj in value:
                if obj not in schema._declared_fields:
                    raise InvalidField(
                        "{} has no attribute {}".format(schema.__name__, obj)
                    )

        return result

    _RELATIONSHIP_SEPARATOR = "."

    @property
    def sorting(self):
        """
        Return fields to sort by, resolving nested relationships properly.

        :return list: a list of sorting information

        Example return value::
            [
                {'field': 'created_at', 'order': 'desc'},
            ]
        """
        if not self.qs.get("sort"):
            return []

        sorting_results = []
        for sort_field in self.qs["sort"].split(","):
            current_schema = self.schema
            order = "desc" if sort_field.startswith("-") else "asc"
            sort_field: str = sort_field.lstrip("-")

            if self._RELATIONSHIP_SEPARATOR not in sort_field:
                if sort_field not in self.schema._declared_fields:
                    raise InvalidSort(
                        f"{self.schema.__name__} has no attribute {sort_field}"
                    )

                if sort_field in get_relationships(self.schema):
                    raise InvalidSort(
                        f"{sort_field} is a relationship field and requires an attribute to sort on"
                    )

                field = get_model_field(self.schema, sort_field)
                sorting_results.append({"field": field, "order": order})

            else:
                fields = sort_field.split(self._RELATIONSHIP_SEPARATOR)

                for idx, field in enumerate(fields):
                    is_last = idx == len(fields) - 1
                    relationships = get_relationships(current_schema)

                    if field in relationships:
                        if is_last:
                            raise InvalidSort(
                                f"{field} is a relationship field and requires an attribute to sort on"
                            )
                        type_ = current_schema._declared_fields[field].__dict__["type_"]
                        current_schema = get_schema_from_type(type_)
                    elif is_last:
                        if field not in current_schema._declared_fields:
                            raise InvalidSort(
                                f"{current_schema.__name__} has no attribute {field}"
                            )
                        field = get_model_field(current_schema, field)
                    else:
                        raise InvalidSort(
                            f"You can't sort on {field} because it is not a relationship field"
                        )

                sorting_results.append({"field": sort_field, "order": order})

        return sorting_results

    @property
    def include(self):
        """Return fields to include

        :return list: a list of include information
        """
        include_param = self.qs.get("include", [])

        if current_app.config.get("MAX_INCLUDE_DEPTH") is not None:
            for include_path in include_param:
                if (
                    len(include_path.split("."))
                    > current_app.config["MAX_INCLUDE_DEPTH"]
                ):
                    raise InvalidInclude(
                        "You can't use include through more than {} relationships".format(
                            current_app.config["MAX_INCLUDE_DEPTH"]
                        )
                    )

        return include_param.split(",") if include_param else []
