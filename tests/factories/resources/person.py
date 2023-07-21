from flask import make_response

from flask_rest_jsonapi_next import (
    JsonApiException,
    ResourceDetail,
    ResourceList,
    ResourceRelationship,
)

from ..models import APP_DB, Person, PersonSchema
from .commons import dummy_decorator


class PersonList(ResourceList):
    def before_create_object(self, data, view_kwargs):
        pass

    schema = PersonSchema
    data_layer = {
        "model": Person,
        "session": APP_DB.session,
        "methods": {"before_create_object": before_create_object},
    }
    get_decorators = [dummy_decorator()]
    post_decorators = [dummy_decorator()]
    get_schema_kwargs = dict()
    post_schema_kwargs = dict()


class PersonDetail(ResourceDetail):
    def before_update_object(self, obj, data, view_kwargs):
        pass

    def before_delete_object(self, obj, view_kwargs):
        pass

    schema = PersonSchema
    data_layer = {
        "model": Person,
        "session": APP_DB.session,
        "url_field": "person_id",
        "methods": {
            "before_update_object": before_update_object,
            "before_delete_object": before_delete_object,
        },
    }
    get_decorators = [dummy_decorator()]
    patch_decorators = [dummy_decorator()]
    delete_decorators = [dummy_decorator()]
    get_schema_kwargs = dict()
    patch_schema_kwargs = dict()
    delete_schema_kwargs = dict()


class PersonComputersRelationship(ResourceRelationship):
    schema = PersonSchema
    data_layer = {
        "session": APP_DB.session,
        "model": Person,
        "url_field": "person_id",
    }
    get_decorators = [dummy_decorator()]
    post_decorators = [dummy_decorator()]
    patch_decorators = [dummy_decorator()]
    delete_decorators = [dummy_decorator()]


class PersonListRaiseJsonapiExc(ResourceList):
    def get(self):
        raise JsonApiException("", "")


class PersonListRaiseExc(ResourceList):
    def get(self):
        raise Exception()


class PersonListMakeResponse(ResourceList):
    def get(self):
        return make_response("")


class PersonListMakeResponseNoSchema(ResourceList):
    data_layer = {
        "model": PermissionError,
        "session": APP_DB.session,
    }

    def get(self):
        return make_response("")
