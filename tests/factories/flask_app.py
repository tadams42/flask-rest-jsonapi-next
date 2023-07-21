import pytest
from flask import Blueprint, Flask

from flask_rest_jsonapi_next import Api

from .resources import (
    ComputerDetail,
    ComputerList,
    ComputerOwnerRelationship,
    PersonComputersRelationship,
    PersonDetail,
    PersonList,
    PersonListMakeResponse,
    PersonListMakeResponseNoSchema,
    PersonListRaiseExc,
    PersonListRaiseJsonapiExc,
    StringJsonAttributePersonDetail,
    StringJsonAttributePersonList,
)


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


@pytest.fixture
def client(app):
    yield app.test_client()


@pytest.fixture
def api_blueprint(client):
    bp = Blueprint("api", __name__)
    yield bp


@pytest.fixture
def api(api_blueprint):
    return Api(blueprint=api_blueprint)


@pytest.fixture
def register_routes(client, api, app, api_blueprint):
    api.route(PersonList, "person_list", "/persons")
    api.route(PersonDetail, "person_detail", "/persons/<int:person_id>")
    api.route(
        PersonComputersRelationship,
        "person_computers",
        "/persons/<int:person_id>/relationships/computers",
    )
    api.route(
        PersonComputersRelationship,
        "person_computers_error",
        "/persons/<int:person_id>/relationships/computer",
    )
    api.route(
        PersonListRaiseJsonapiExc,
        "person_list_jsonapiexception",
        "/persons_jsonapiexception",
    )
    api.route(PersonListRaiseExc, "person_list_exception", "/persons_exception")
    api.route(PersonListMakeResponse, "person_list_response", "/persons_response")
    api.route(
        PersonListMakeResponseNoSchema,
        "person_list_without_schema",
        "/persons_without_schema",
    )
    api.route(
        ComputerList,
        "computer_list",
        "/computers",
        "/persons/<int:person_id>/computers",
    )
    api.route(ComputerDetail, "computer_detail", "/computers/<int:id>")
    api.route(
        ComputerOwnerRelationship,
        "computer_owner",
        "/computers/<int:id>/relationships/owner",
    )
    api.route(
        StringJsonAttributePersonList,
        "string_json_attribute_person_list",
        "/string_json_attribute_persons",
    )
    api.route(
        StringJsonAttributePersonDetail,
        "string_json_attribute_person_detail",
        "/string_json_attribute_persons/<int:person_id>",
    )


@pytest.fixture
def api_middleware(app, api, register_routes):
    api.init_app(app)


@pytest.fixture()
def get_object_mock():
    class get_object(object):
        foo = type(
            "foo",
            (object,),
            {
                "property": type(
                    "prop",
                    (object,),
                    {"mapper": type("map", (object,), {"class_": "test"})()},
                )()
            },
        )()

        def __init__(self, kwargs):
            pass

    return get_object


@pytest.fixture()
def wrong_data_layer():
    class WrongDataLayer(object):
        pass

    yield WrongDataLayer
