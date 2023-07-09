from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema
from sqlalchemy import Column, ForeignKey, Integer, String

from .db import Base


class Computer(Base):
    __tablename__ = "computer"

    id = Column(Integer, primary_key=True)
    serial = Column(String, nullable=False)
    person_id = Column(Integer, ForeignKey("person.person_id"))


class ComputerSchema(Schema):
    class Meta:
        type_ = "computer"
        self_view = "api.computer_detail"
        self_view_kwargs = {"id": "<id>"}

    id = fields.Integer(as_string=True)
    serial = fields.Str(required=True)
    owner = Relationship(
        attribute="person",
        dump_default=None,
        load_default=None,
        related_view="api.person_detail",
        related_view_kwargs={"person_id": "<person.person_id>"},
        schema="PersonSchema",
        id_field="person_id",
        type_="person",
    )
