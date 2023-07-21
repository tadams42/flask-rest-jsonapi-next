from flask_rest_jsonapi_next import ResourceDetail, ResourceList, ResourceRelationship

from ..models import APP_DB, Computer, ComputerSchema, Person


class ComputerList(ResourceList):
    def query(self, view_kwargs):
        if view_kwargs.get("person_id") is not None:
            return (
                self.session.query(Computer)
                .join(Person)
                .filter_by(person_id=view_kwargs["person_id"])
            )
        return self.session.query(Computer)

    schema = ComputerSchema
    data_layer = {
        "model": Computer,
        "session": APP_DB.session,
        "methods": {"query": query},
    }


class ComputerDetail(ResourceDetail):
    schema = ComputerSchema
    data_layer = {
        "model": Computer,
        "session": APP_DB.session,
    }
    methods = ["GET", "PATCH"]


class ComputerOwnerRelationship(ResourceRelationship):
    schema = ComputerSchema
    data_layer = {
        "session": APP_DB.session,
        "model": Computer,
    }
