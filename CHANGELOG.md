# CHANGELOG

## 0.33.0 (fork-0.33.0) (unreleased)

- supporting Flask only >= 2.2.0
  - Flask dropped metaclasses in favor of `__init_subclass__` (which is great) but
    our `Resource` class relied on metaclasses too
  - supporting both mechanisms, metaclasses and `__init_subclass__`, is not feasible,
    thus dropping support for older flask versions

## 0.32.8 (fork-0.32.8) (2022-02-15)

- fix: PATCH was not rising ValidationError for fields with `required=True`, when those
  fields were missing from `request.body`

## 0.32.7 (fork-0.32.7) (2022-02-15)

- fix: sparse fields were not applied correctly

## 0.32.6 (fork-0.32.6) (2022-03-15)

- feat: added `register_at` parameter to `Api.__init__()`
- fix: `Api` shouldn't use `Flask.config.APLICATION_ROOT` for registering blueprint;
  this variable was not meant for that purpose

## 0.32.5 (fork-0.32.5) (2022-02-16)

- fix: API blueprint should respech `Flask.config.APPLICATION_ROOT`

## 0.32.4 (fork-0.32.4) (2022-02-07)

- fix: more problems with content negotiation: API was allowing different `Accept`
  header, but was still forcing `Content-Type: application/vnd.api+json` in responses

## 0.32.3 (fork-0.32.3) (2022-02-04)

- fix: marshmallow3 compatibility - `fields.List.container` attribute no longer exists

## 0.32.2 (fork-0.32.2) (2022-01-21)

- fix: API returns 404 on `/resource/<int:id>` routes when no object is found

## 0.32.1 (fork-0.32.1) (2022-01-04)

- feat: allows "multipart/form-data" content type on all POST and PATCH requests
  - this is not ideal, but we need it to support file uploads for some of our APIs
  - in the future, proper content type negotiation must be implemented

## 0.32.0 (fork-0.32.0) (2022-01-03)

- feat: while app exception handling and JSON:API error responses
- feat: use all decorators from all Resource subclasses
- feat: POST and PATCH schemas can be separately declared from `Resource.schema`
- optional call to `model.validate()` in data layer
- support for CSV in simple filter URL parameters (`?filter[foo]=1,2,3`)
- use `rapidjson` if it is installed

## v0.31.2 (2021-12-28)

- initial release based on
  [miLibris/flask-rest-jsonapi](https://github.com/miLibris/flask-rest-jsonapi) `v0.31.2
  (a4ff3f4d5be78071f015efe003e976d31d4eba10)`
