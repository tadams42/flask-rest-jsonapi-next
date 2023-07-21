from marshmallow import Schema as MarshmallowSchema
from marshmallow_jsonapi import fields
from sqlalchemy import Column, ForeignKey, Integer, String

from .db import Base


class PersonSingleTag(Base):
    __tablename__ = "person_single_tag"

    id = Column(Integer, ForeignKey("person.person_id"), primary_key=True, index=True)
    key = Column(String)
    value = Column(String)


class PersonSingleTagSchema(MarshmallowSchema):
    class Meta:
        type_ = "person_single_tag"

    id = fields.Str(load_only=True)
    key = fields.Str()
    value = fields.Str()
