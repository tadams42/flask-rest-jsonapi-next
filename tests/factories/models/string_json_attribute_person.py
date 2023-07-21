from marshmallow import Schema as MarshmallowSchema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from sqlalchemy import Column, DateTime, Integer, String

from .db import Base, MagicJSON


class StringJsonAttributePerson(Base):
    __tablename__ = "string_json_attribute_person"

    person_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    birth_date = Column(DateTime)
    # This model uses a String type for "json_tags" to avoid dependency on a nonstandard
    # SQL type in testing, while still demonstrating support
    address = Column(MagicJSON)


class AddressSchema(MarshmallowSchema):
    street = fields.String(required=True)
    city = fields.String(required=True)
    state = fields.String(load_default="NC")
    zip = fields.String(required=True)


class StringJsonAttributePersonSchema(Schema):
    class Meta:
        type_ = "string_json_attribute_person"
        self_view = "api.string_json_attribute_person_detail"
        self_view_kwargs = {"person_id": "<id>"}

    id = fields.Integer(as_string=True, attribute="person_id")
    name = fields.Str(required=True)
    birth_date = fields.DateTime()
    address = fields.Nested(AddressSchema, many=False)
