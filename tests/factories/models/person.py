from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from .db import Base
from .person_single_tag import PersonSingleTagSchema
from .person_tag import PersonTagSchema


class Person(Base):
    __tablename__ = "person"

    person_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    birth_date = Column(DateTime)
    computers = relationship("Computer", backref="person")
    tags = relationship(
        "PersonTag", cascade="save-update, merge, delete, delete-orphan"
    )
    single_tag = relationship(
        "PersonSingleTag",
        uselist=False,
        cascade="save-update, merge, delete, delete-orphan",
    )


class PersonSchema(Schema):
    class Meta:
        type_ = "person"
        self_view = "api.person_detail"
        self_view_kwargs = {"person_id": "<id>"}

    id = fields.Integer(as_string=True, attribute="person_id")
    name = fields.Str(required=True)
    birth_date = fields.DateTime()
    computers = Relationship(
        related_view="api.computer_list",
        related_view_kwargs={"person_id": "<person_id>"},
        schema="ComputerSchema",
        type_="computer",
        many=True,
    )

    tags = fields.Nested(PersonTagSchema, many=True)
    single_tag = fields.Nested(PersonSingleTagSchema)
