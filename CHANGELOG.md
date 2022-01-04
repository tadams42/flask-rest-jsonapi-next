# CHANGELOG

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
