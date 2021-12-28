[![PyPi Status](https://badge.fury.io/py/flask-rest-jsonapi-next.svg)](https://badge.fury.io/py/flask-rest-jsonapi-next)
[![Build Status](https://travis-ci.org/tadams42/flask-rest-jsonapi-next.svg)](https://app.travis-ci.com/tadams42/flask-rest-jsonapi-next)
[![Coverage Status](https://coveralls.io/repos/github/tadams42/flask-rest-jsonapi-next/badge.svg)](https://coveralls.io/github/tadams42/flask-rest-jsonapi-next)
[![Documentation Status](https://readthedocs.org/projects/flask-rest-jsonapi-next/badge/?version=latest)](http://flask-rest-jsonapi-next.readthedocs.io/en/latest/?badge=latest)

# flask-rest-jsonapi-next


!!! note This is a fork of [miLibris/flask-rest-jsonapi](https://github.com/miLibris/flask-rest-jsonapi) project

    Initial release of `flask-rest-jsonapi-next` is built from
    `miLibris/flask-rest-jsonapi`, `v0.31.2 (a4ff3f4d5be78071f015efe003e976d31d4eba10)`

`flask-rest-jsonapi-next` is a flask extension for building REST APIs. It combines the
power of [Flask-Restless](https://flask-restless.readthedocs.io/) and the flexibility of
[Flask-RESTful](https://flask-restful.readthedocs.io/) around a strong specification
[JSON:API 1.0](http://jsonapi.org/). This framework is designed to quickly build REST
APIs and fit the complexity of real life projects with legacy data and multiple data
storages.

## Install

```sh
pip install flask-rest-jsonapi-next
```

## A minimal API

```py
# -*- coding: utf-8 -*-

from flask import Flask
from flask_rest_jsonapi_next import Api, ResourceDetail, ResourceList
from flask_sqlalchemy import SQLAlchemy
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

# Create the Flask application and the Flask-SQLAlchemy object.
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

# Create model
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

# Create the database.
db.create_all()

# Create schema
class PersonSchema(Schema):
    class Meta:
        type_ = 'person'
        self_view = 'person_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'person_list'

    id = fields.Integer(as_string=True, dump_only=True)
    name = fields.Str()

# Create resource managers
class PersonList(ResourceList):
    schema = PersonSchema
    data_layer = {'session': db.session,
                    'model': Person}

class PersonDetail(ResourceDetail):
    schema = PersonSchema
    data_layer = {'session': db.session,
                    'model': Person}

# Create the API object
api = Api(app)
api.route(PersonList, 'person_list', '/persons')
api.route(PersonDetail, 'person_detail', '/persons/<int:id>')

# Start the flask loop
if __name__ == '__main__':
    app.run()
```

This example provides the following API structure:

| URL                        | method | endpoint      | Usage                       |
| -------------------------- | ------ | ------------- | --------------------------- |
| `/persons`                 | GET    | person_list   | Get a collection of persons |
| `/persons`                 | POST   | person_list   | Create a person             |
| `/persons/<int:person_id>` | GET    | person_detail | Get person details          |
| `/persons/<int:person_id>` | PATCH  | person_detail | Update a person             |
| `/persons/<int:person_id>` | DELETE | person_detail | Delete a person             |

## flask-rest-jsonapi-next vs [Flask-RESTful](http://flask-restful-cn.readthedocs.io/en/0.3.5/a)

- In contrast to Flask-RESTful, flask-rest-jsonapi-next provides a default
  implementation of get, post, patch and delete methods around a strong specification
  JSONAPI 1.0. Thanks to this you can build REST API very quickly.
- flask-rest-jsonapi-next is as flexible as Flask-RESTful. You can rewrite every default
  method implementation to make custom work like distributing object creation.

## flask-rest-jsonapi-next vs [Flask-Restless](https://flask-restless.readthedocs.io/en/stable/)

- flask-rest-jsonapi-next is a real implementation of JSONAPI 1.0 specification.  So in
  contrast to Flask-Restless, flask-rest-jsonapi-next forces you to create a real
  logical abstration over your data models with
  [Marshmallow](https://marshmallow.readthedocs.io/en/latest/). So you can create
  complex resource over your data.
- In contrast to Flask-Restless, flask-rest-jsonapi-next can use any ORM or data storage
  through the data layer concept, not only [SQLAlchemy](http://www.sqlalchemy.org/). A
  data layer is a CRUD interface between your resource and one or more data storage so
  you can fetch data from any data storage of your choice or create resource that use
  multiple data storages.
- Like I said previously, flask-rest-jsonapi-next is a real implementation of JSONAPI
  1.0 specification. So in contrast to Flask-Restless you can manage relationships via
  REST. You can create dedicated URL to create a CRUD API to manage relationships.
- Plus flask-rest-jsonapi-next helps you to design your application with strong
  separation between resource definition (schemas), resource management (resource class)
  and route definition to get a great organization of your source code.
- In contrast to Flask-Restless, flask-rest-jsonapi-next is highly customizable. For
  example you can entirely customize your URLs, define multiple URLs for the same
  resource manager, control serialization parameters of each method and lots of very
  useful parameters.
- Finally in contrast to Flask-Restless, flask-rest-jsonapi-next provides a great error
  handling system according to JSONAPI 1.0. Plus the exception handling system really
  helps the API developer to quickly find missing resources requirements.

## Documentation

Documentation available here:
[http://flask-rest-jsonapi-next.readthedocs.io/en/latest/](http://flask-rest-jsonapi-next.readthedocs.io/en/latest/)

## Thanks

Flask, marshmallow, marshmallow_jsonapi, sqlalchemy, Flask-RESTful and Flask-Restless
are awesome projects. These libraries gave me inspiration to create
flask-rest-jsonapi-next, so huge thanks to authors and contributors.
