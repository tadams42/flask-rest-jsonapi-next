from flask_rest_jsonapi_next import ResourceDetail, ResourceList

from ..models import APP_DB, StringJsonAttributePerson, StringJsonAttributePersonSchema


class StringJsonAttributePersonDetail(ResourceDetail):
    schema = StringJsonAttributePersonSchema
    data_layer = {
        "session": APP_DB.session,
        "model": StringJsonAttributePerson,
    }


class StringJsonAttributePersonList(ResourceList):
    schema = StringJsonAttributePersonSchema
    data_layer = {
        "session": APP_DB.session,
        "model": StringJsonAttributePerson,
    }
