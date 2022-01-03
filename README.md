# flask-rest-jsonapi-next

[![PyPi Status](https://badge.fury.io/py/flask-rest-jsonapi-next.svg)](https://badge.fury.io/py/flask-rest-jsonapi-next)
[![license](https://img.shields.io/pypi/l/flask-rest-jsonapi-next.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://app.travis-ci.com/tadams42/flask-rest-jsonapi-next.svg?branch=development)](https://app.travis-ci.com/tadams42/flask-rest-jsonapi-next)
[![Coverage Status](https://coveralls.io/repos/github/tadams42/flask-rest-jsonapi-next/badge.svg?branch=development)](https://coveralls.io/github/tadams42/flask-rest-jsonapi-next?branch=development)
[![Documentation Status](https://readthedocs.org/projects/flask-rest-jsonapi-next/badge/?version=latest)](http://flask-rest-jsonapi-next.readthedocs.io/en/latest/?badge=latest)
[![python_versions](https://img.shields.io/pypi/pyversions/flask-rest-jsonapi-next.svg)](https://pypi.org/project/flask-rest-jsonapi-next/)

This is a fork of [miLibris/flask-rest-jsonapi](https://github.com/miLibris/flask-rest-jsonapi) project.

`flask-rest-jsonapi-next` is a flask extension for building REST APIs around a strong specification
[JSON:API 1.0](http://jsonapi.org/).

Documentation: [http://flask-rest-jsonapi-next.readthedocs.io/en/latest/](http://flask-rest-jsonapi-next.readthedocs.io/en/latest/)

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

## Thanks

Flask, marshmallow, marshmallow_jsonapi, sqlalchemy, Flask-RESTful and Flask-Restless
are awesome projects. These libraries gave me inspiration to create
flask-rest-jsonapi-next, so huge thanks to authors and contributors.
