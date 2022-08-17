Features
========

Upstream features
-----------------

flask-rest-jsonapi-next has lots of features:

* Relationship management
* Powerful filtering
* Include related objects
* Sparse fieldsets
* Pagination
* Sorting
* Permission management
* OAuth support

About fork
----------

Initial release of ``flask-rest-jsonapi-next`` is built from
``miLibris/flask-rest-jsonapi``, ``v0.31.2 (a4ff3f4d5be78071f015efe003e976d31d4eba10)``

Exception handling
__________________

Upstream handles all errors produced by API and generates JSON:API error responses.

This fork implements a bit broader error handling:

- all application errors (not just the ones from API routes) are intercepted and
  returned as JSON:API error responses
- in some cases, error responses will contain more details than upstream's
- we provide simple way to extending this error handling and conversion by allowing
  for converters for custom exception types
- this functionality of intercepting all app's errors currently can't neither be
  disabled nor circumvented (in the future, we'd might implement more of opt-in
  behavior that would be compatible with how upstream does things)

decorators in Resource
______________________

All decorators found in `Resource` inheritance path are applied to that resource.
Upstream applies only leaf class decorators

.. code-block:: python

   from flask_rest_jsonapi_next import ResourceList

   class A(ResourceList):
       decorators = (dec1,)

   class MyListResource(B):
       pass

In upstream:

.. code-block:: python

   MyListResource.decorators == (check_headers, )

and in  flask_rest_jsonapi_next

.. code-block:: python

   MyListResource.decorators == (check_headers, dec1, )

configurable POST and PATCH Resource schema
___________________________________________

``Resource`` subclasses can have following optional attributes:

- ``post_schema``
- ``post_response_schema``
- ``patch_schema``
- ``patch_response_schema``

``Resource.post()`` and ``Resource.patch()`` had been adjusted to use these.

Optional support for model.validate()
_____________________________________

If model instance has ``validate()`` method, then our modified `SqlalchemyDataLaye`r`
data layer will call this method before ``db.session.commit()``.

less strict requirements on `Content-Type` HTTP header
______________________________________________________

For ``Content-Type`` we allow allow both ``application/vnd.api+json`` and ``application/json``
values.

This is because at least one of our frontend apps is known not to use correct JSON:API
value for ``Content-Type`` header.

In the future, proper content negotiation will probably be implemented.

support IN operator in simple filters
_____________________________________

Original implementation supports simple filter syntax:

.. code-block:: http

   GET ...?filter[foo]=bar

which is equivalent to:

.. code-block:: sql

   where foo = 'bar'

We'd added support for coma separated list of values like this:

.. code-block:: http

   GET ...?filter[foo]=1,2

which is equivalent to:

.. code-block:: sql

   where foo IN (1, 2)

Compared to other similar projects
----------------------------------

Flask-RESTful
_____________

`Flask-RESTful <http://flask-restful-cn.readthedocs.io/en/0.3.5/a>`_

- In contrast to Flask-RESTful, flask-rest-jsonapi-next provides a default
  implementation of get, post, patch and delete methods around a strong specification
  JSONAPI 1.0. Thanks to this you can build REST API very quickly.
- flask-rest-jsonapi-next is as flexible as Flask-RESTful. You can rewrite every default
  method implementation to make custom work like distributing object creation.

Flask-Restless
______________

`Flask-Restless <https://flask-restless.readthedocs.io/en/stable/>`_

- flask-rest-jsonapi-next is a real implementation of JSONAPI 1.0 specification.  So in
  contrast to Flask-Restless, flask-rest-jsonapi-next forces you to create a real
  logical abstraction over your data models with `Marshmallow
  <https://marshmallow.readthedocs.io/en/latest/>`_. So you can create complex resource
  over your data.
- In contrast to Flask-Restless, flask-rest-jsonapi-next can use any ORM or data storage
  through the data layer concept, not only `SQLAlchemy <http://www.sqlalchemy.org/>`_. A
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
