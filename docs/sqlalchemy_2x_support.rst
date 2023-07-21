.. _sqlalchemy_2x_support:

Working with SQLAlchemy 2.x data layers
=======================================

`_SQLAlchemy changelog <https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html#change-c4886b74af98b72892877aefa7d6a6a4>`_
states:

> Loader options no longer accept strings for attribute names. The long-documented
> approach of using ``Class.attrname`` for loader option targets is now standard.

Assuming following classes:

.. code-block:: python

    class Person(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String)


    class Computer(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        person_id = db.Column(db.Integer, db.ForeignKey('person.id'))
        person = db.relationship('Person', backref=db.backref('computers'))

Then in SQLAlchemy 1.x, following expressions both worked:

.. code-block:: python

    import sqlalchemy as sa
    from sqlalchemy import orm

    query = sa.select(Computer).options(orm.joinedload("person"))
    query = sa.select(Computer).options(orm.joinedload(Computer.person))

In SQLAlchemy 2.x, only this works:

.. code-block:: python

    import sqlalchemy as sa
    from sqlalchemy import orm

    query = sa.select(Computer).options(orm.joinedload(Computer.person))

``flask-rest-jsonapi-next`` data layer is using ``orm.joinedload()`` to eagerly load
objects for requests with ``?include`` URL parameter and thus tries to prevent N + 1
query problems for these requests.

To do that, it relies on marshmallow schema for given resource and ability of SQLAlchemy
to place "random" strings it gets as argument of ``orm.joinedload()`` into proper
context of mapped entity. This is no longer possible without having more context in
schema itself.

In short assuming we have following schema in our code:

.. code-block:: python

    class ComputerSchema(Schema):
        class Meta:
            type_ = 'computer'
            # ...

        id = fields.Integer(as_string=True, dump_only=True)
        person = Relationship(...)

And we make following request:

.. code-block::

    GET /api/computers?include=person

Everything except eager loading will still work and we will get expected response. But,
in contrary to app that is using SQLAlchemy 1.x data layer, above request will generate
additional SQL query for each returned ``computer``.

Also, ``flask-rest-jsonapi-next`` will emit helpful warning:

.. code-block::

    FlaskRestJsonApiNextWarning: When using SQLAlchemy 2.x, resource schema classes must
    have 'SchemaClass.Meta.model' attribute. Without this, eager loading of included
    objects can't work and is disabled. Without eager loading, app may run into N + 1
    query problem which will affect performance. Warning for:
    <class 'may.app.package.ComputerSchema'>.person

To get eager loading back, each schema in your codebase must add ``Meta.model``
attribute like this:

.. code-block:: python

    class ComputerSchema(Schema):
        class Meta:
            type_ = 'computer'
            # ...

            # Following is required for SQLAlchemy 2.x eager loading
            model = Computer

        id = fields.Integer(as_string=True, dump_only=True)
        person = Relationship(...)
