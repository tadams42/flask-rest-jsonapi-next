"""Helpers to deal with marshmallow schemas"""

import copy
from typing import Optional, Set, Tuple

from marshmallow import class_registry
from marshmallow.base import SchemaABC
from marshmallow_jsonapi.fields import List, Nested, Relationship

from .exceptions import InvalidInclude


def compute_schema(schema_cls, default_kwargs, qs, include):
    """Compute a schema around compound documents and sparse fieldsets

    :param Schema schema_cls: the schema class
    :param dict default_kwargs: the schema default kwargs
    :param QueryStringManager qs: qs
    :param list include: the relation field to include data from

    :return Schema schema: the schema computed
    """
    # manage include_data parameter of the schema
    schema_kwargs = default_kwargs
    schema_kwargs["include_data"] = tuple()

    # collect sub-related_includes
    related_includes = {}

    if include:
        for include_path in include:
            field = include_path.split(".")[0]

            if field not in schema_cls._declared_fields:
                raise InvalidInclude(
                    "{} has no attribute {}".format(schema_cls.__name__, field)
                )
            elif not isinstance(schema_cls._declared_fields[field], Relationship):
                raise InvalidInclude(
                    "{} is not a relationship attribute of {}".format(
                        field, schema_cls.__name__
                    )
                )

            schema_kwargs["include_data"] += (field,)
            if field not in related_includes:
                related_includes[field] = []
            if "." in include_path:
                related_includes[field] += [".".join(include_path.split(".")[1:])]

    only = _compute_sparse(schema_cls, default_kwargs, qs, include)
    if only is not None:
        schema_kwargs["only"] = only

    # create base schema instance
    schema = schema_cls(**schema_kwargs)

    # manage compound documents
    if include:
        for include_path in include:
            field = include_path.split(".")[0]
            relation_field = schema.declared_fields[field]
            related_schema_cls = schema.declared_fields[field].__dict__[
                "_Relationship__schema"
            ]
            related_schema_kwargs = {}
            if "context" in default_kwargs:
                related_schema_kwargs["context"] = default_kwargs["context"]
            if isinstance(related_schema_cls, SchemaABC):
                related_schema_kwargs["many"] = related_schema_cls.many
                related_schema_cls = related_schema_cls.__class__
            if isinstance(related_schema_cls, str):
                related_schema_cls = class_registry.get_class(related_schema_cls)
            related_schema = compute_schema(
                related_schema_cls,
                related_schema_kwargs,
                qs,
                related_includes[field] or None,
            )
            relation_field.__dict__["_Relationship__schema"] = related_schema

    return schema


def get_model_field(schema, field):
    """Get the model field of a schema field

    :param Schema schema: a marshmallow schema
    :param str field: the name of the schema field
    :return str: the name of the field in the model
    """
    if schema._declared_fields.get(field) is None:
        raise Exception("{} has no attribute {}".format(schema.__name__, field))

    if schema._declared_fields[field].attribute is not None:
        return schema._declared_fields[field].attribute
    return field


def get_nested_fields(schema, model_field=False):
    """Return nested fields of a schema to support a join

    :param Schema schema: a marshmallow schema
    :param boolean model_field: whether to extract the model field for the nested fields
    :return list: list of nested fields of the schema
    """

    nested_fields = []
    for key, value in schema._declared_fields.items():
        if isinstance(value, List):
            nested_fields.append(key)
        elif isinstance(value, Nested):
            nested_fields.append(key)

    if model_field is True:
        nested_fields = [get_model_field(schema, key) for key in nested_fields]

    return nested_fields


def get_relationships(schema, model_field=False):
    """Return relationship fields of a schema

    :param Schema schema: a marshmallow schema
    :param list: list of relationship fields of a schema
    """
    relationships = [
        key
        for (key, value) in schema._declared_fields.items()
        if isinstance(value, Relationship)
    ]

    if model_field is True:
        relationships = [get_model_field(schema, key) for key in relationships]

    return relationships


def get_related_schema(schema, field):
    """Retrieve the related schema of a relationship field

    :param Schema schema: the schema to retrieve le relationship field from
    :param field: the relationship field
    :return Schema: the related schema
    """
    return schema._declared_fields[field].__dict__["_Relationship__schema"]


def get_schema_from_type(resource_type):
    """Retrieve a schema from the registry by his type

    :param str type_: the type of the resource
    :return Schema: the schema class
    """
    for cls_name, cls in class_registry._registry.items():
        try:
            if cls[0].opts.type_ == resource_type:
                return cls[0]
        except Exception:
            pass

    raise ValueError("Couldn't find schema for type: {}".format(resource_type))


def get_schema_field(schema, field):
    """Get the schema field of a model field

    :param Schema schema: a marshmallow schema
    :param str field: the name of the model field
    :return str: the name of the field in the schema
    """
    schema_fields_to_model = {
        key: get_model_field(schema, key)
        for (key, value) in schema._declared_fields.items()
    }
    for key, value in schema_fields_to_model.items():
        if value == field:
            return key

    raise ValueError("Couldn't find schema field from {}".format(field))


def _compute_sparse(
    schema_cls, default_kwargs, qs, include
) -> Optional[Tuple[str, ...]]:
    """
    Compute "only" keyword argument for marshmallow.Schema.

    We need this because following has no effect:

        schema = FooSchema()
        schema.only = ("field1", "field2", ...)

    marsmallow.Schema.only should really, really, really be private attribute or
    read-only property: setting it's value after instance had been __init__-ialized
    has no effect.
    """
    # manage include_data parameter of the schema
    schema_kwargs = {k: v for k, v in (default_kwargs or dict()).items()}

    only = schema_kwargs.get("only")
    # make sure id field is in only parameter unless marshmallow will raise an Exception
    if only is not None and "id" not in only:
        only = set(only)
        only.add("id")
        schema_kwargs["only"] = tuple(only)

    schema = schema_cls(**schema_kwargs)

    # manage sparse fieldsets
    if schema.opts.type_ in qs.fields:
        only = set(schema.declared_fields.keys()) & set(qs.fields[schema.opts.type_])
        if schema.only:
            only &= set(schema.only)

        if only is not None and "id" not in only:
            only.add("id")

    # manage compound documents
    if include and only is not None:
        only = only.union(set(include))

    if only is not None:
        return tuple(only)

    return None
