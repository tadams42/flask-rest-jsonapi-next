from marshmallow import Schema as MarshmallowSchema
from marshmallow_jsonapi import fields
from sqlalchemy import Column, ForeignKey, Integer, String

from .db import Base


class PersonTag(Base):
    __tablename__ = "person_tag"

    id = Column(Integer, ForeignKey("person.person_id"), primary_key=True, index=True)
    key = Column(String, primary_key=True)
    value = Column(String, primary_key=True)


class PersonTagSchema(MarshmallowSchema):
    class Meta:
        type_ = "person_tag"

    id = fields.Str(load_only=True)
    key = fields.Str()
    value = fields.Str()
