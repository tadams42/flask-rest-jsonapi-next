import pytest
from marshmallow import ValidationError

import flask_rest_jsonapi_next.decorators
from flask_rest_jsonapi_next import (
    Api,
    JsonApiException,
    ResourceDetail,
    ResourceList,
    SqlalchemyDataLayer,
)


def test_json_api_exception():
    JsonApiException(None, None, title="test", status="test")


def test_api(app, person_list):
    api = Api(app)
    api.route(person_list, "person_list", "/persons", "/person_list")
    api.init_app()


def test_api_resources(app, person_list):
    api = Api()
    api.route(person_list, "person_list2", "/persons", "/person_list")
    api.init_app(app)


def test_check_method_requirements(monkeypatch):
    self = type("self", (object,), dict())
    request = type("request", (object,), dict(method="GET"))
    monkeypatch.setattr(flask_rest_jsonapi_next.decorators, "request", request)
    with pytest.raises(Exception):
        flask_rest_jsonapi_next.decorators.check_method_requirements(lambda: 1)(self())


def test_resource(app, db, person_model, person_schema, monkeypatch):
    def schema_load_mock(*args, **kwargs):
        raise ValidationError(dict(errors=[dict(status=None, title=None)]))

    with app.app_context():
        query_string = {"page[slumber]": "3"}
        app = type("app", (object,), dict(config=dict(DEBUG=True)))
        headers = {"Content-Type": "application/vnd.api+json"}
        request = type(
            "request",
            (object,),
            dict(method="POST", headers=headers, get_json=dict, args=query_string),
        )
        dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
        rl = ResourceList()
        rd = ResourceDetail()
        rl._data_layer = dl
        rl.schema = person_schema
        rd._data_layer = dl
        rd.schema = person_schema
        monkeypatch.setattr(flask_rest_jsonapi_next.resource, "request", request)
        monkeypatch.setattr(flask_rest_jsonapi_next.decorators, "current_app", app)
        monkeypatch.setattr(flask_rest_jsonapi_next.decorators, "request", request)
        monkeypatch.setattr(rl.schema, "load", schema_load_mock)
        r = super(flask_rest_jsonapi_next.resource.Resource, ResourceList).__new__(
            ResourceList
        )
        with pytest.raises(Exception):
            r.dispatch_request()

        with pytest.raises(ValidationError):
            rl.post()
        with pytest.raises(ValidationError):
            rd.patch()


def test_resource_args(app):
    class TestResource(ResourceDetail):
        """
        This fake resource always renders a constructor parameter
        """

        def __init__(self, *args, **kwargs):
            super(TestResource, self).__init__()
            self.constant = args[0]

        def get(self):
            return self.constant

    api = Api(app=app)
    api.route(TestResource, "resource_args", "/resource_args", resource_args=["hello!"])
    api.init_app()
    with app.test_client() as client:
        rv = client.get("/resource_args")
        assert rv.json == "hello!"


def test_resource_kwargs(app):
    class TestResource(ResourceDetail):
        """
        This fake resource always renders a constructor parameter
        """

        def __init__(self, *args, **kwargs):
            super(TestResource, self).__init__()
            self.constant = kwargs.get("constant")

        def get(self):
            return self.constant

    api = Api(app=app)
    api.route(
        TestResource,
        "resource_kwargs",
        "/resource_kwargs",
        resource_kwargs={"constant": "hello!"},
    )
    api.init_app()
    with app.test_client() as client:
        rv = client.get("/resource_kwargs")
        assert rv.json == "hello!"
