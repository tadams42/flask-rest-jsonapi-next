from flask import json
from marshmallow_jsonapi.flask import Relationship


def test_post_relationship_no_data(client, api_middleware, computer, person):
    with client:
        response = client.post(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(dict()),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_post_relationship_not_list_missing_type(
    client, api_middleware, computer, person
):
    payload = {"data": {"id": str(person.person_id)}}

    with client:
        response = client.post(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_post_relationship_not_list_missing_id(
    client, api_middleware, computer, person
):
    payload = {"data": {"type": "person"}}

    with client:
        response = client.post(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_post_relationship_not_list_wrong_type(
    client, api_middleware, computer, person
):
    payload = {"data": {"type": "error", "id": str(person.person_id)}}

    with client:
        response = client.post(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 409, response.json["errors"]


def test_post_relationship_missing_type(client, api_middleware, computer, person):
    payload = {"data": [{"id": str(computer.id)}]}

    with client:
        response = client.post(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_post_relationship_missing_id(client, api_middleware, computer, person):
    payload = {
        "data": [
            {
                "type": "computer",
            }
        ]
    }

    with client:
        response = client.post(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_post_relationship_wrong_type(client, api_middleware, computer, person):
    payload = {"data": [{"type": "error", "id": str(computer.id)}]}

    with client:
        response = client.post(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 409, response.json["errors"]


def test_patch_relationship_no_data(client, api_middleware, computer, person):
    with client:
        response = client.patch(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(dict()),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_patch_relationship_not_list_missing_type(
    client, api_middleware, computer, person
):
    payload = {"data": {"id": str(person.person_id)}}

    with client:
        response = client.patch(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_patch_relationship_not_list_missing_id(
    client, api_middleware, computer, person
):
    payload = {"data": {"type": "person"}}

    with client:
        response = client.patch(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_patch_relationship_not_list_wrong_type(
    client, api_middleware, computer, person
):
    payload = {"data": {"type": "error", "id": str(person.person_id)}}

    with client:
        response = client.patch(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 409, response.json["errors"]


def test_patch_relationship_missing_type(client, api_middleware, computer, person):
    payload = {"data": [{"id": str(computer.id)}]}

    with client:
        response = client.patch(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_patch_relationship_missing_id(client, api_middleware, computer, person):
    payload = {
        "data": [
            {
                "type": "computer",
            }
        ]
    }

    with client:
        response = client.patch(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_patch_relationship_wrong_type(client, api_middleware, computer, person):
    payload = {"data": [{"type": "error", "id": str(computer.id)}]}

    with client:
        response = client.patch(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 409, response.json["errors"]


def test_delete_relationship_no_data(client, api_middleware, computer, person):
    with client:
        response = client.delete(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(dict()),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_delete_relationship_not_list_missing_type(
    client, api_middleware, computer, person
):
    payload = {"data": {"id": str(person.person_id)}}

    with client:
        response = client.delete(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_delete_relationship_not_list_missing_id(
    client, api_middleware, computer, person
):
    payload = {"data": {"type": "person"}}

    with client:
        response = client.delete(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_delete_relationship_not_list_wrong_type(
    client, api_middleware, computer, person
):
    payload = {"data": {"type": "error", "id": str(person.person_id)}}

    with client:
        response = client.delete(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 409, response.json["errors"]


def test_delete_relationship_missing_type(client, api_middleware, computer, person):
    payload = {"data": [{"id": str(computer.id)}]}

    with client:
        response = client.delete(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_delete_relationship_missing_id(client, api_middleware, computer, person):
    payload = {
        "data": [
            {
                "type": "computer",
            }
        ]
    }

    with client:
        response = client.delete(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_delete_relationship_wrong_type(client, api_middleware, computer, person):
    payload = {"data": [{"type": "error", "id": str(computer.id)}]}

    with client:
        response = client.delete(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 409, response.json["errors"]


def test_post_relationship_related_object_not_found(client, api_middleware, person):
    payload = {"data": [{"type": "computer", "id": "2"}]}

    with client:
        response = client.post(
            "/persons/" + str(person.person_id) + "/relationships/computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 404, response.json["errors"]


def test_get_relationship_relationship_field_not_found(client, api_middleware, person):
    with client:
        response = client.get(
            "/persons/" + str(person.person_id) + "/relationships/computer",
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 500, response.json["errors"]


def test_relationship_containing_hyphens(
    client,
    api,
    app,
    person_schema,
    person_computers,
    register_routes,
    computer_schema,
    person,
):
    """
    This is a bit of a hack. Basically, since we can no longer have two attributes that
    read from the same key in Marshmallow 3, we have to create a new Schema and Resource
    here that name their relationship "computers_owned" in order to test hyphenation
    """

    class PersonOwnedSchema(person_schema):
        class Meta:
            exclude = ("computers",)

        computers_owned = Relationship(
            related_view="api.computer_list",
            related_view_kwargs={"person_id": "<person_id>"},
            schema="ComputerSchema",
            type_="computer",
            many=True,
            attribute="computers",
        )

    class PersonComputersOwnedRelationship(person_computers):
        schema = PersonOwnedSchema

    api.route(
        PersonComputersOwnedRelationship,
        "person_computers_owned",
        "/persons/<int:person_id>/relationships/computers-owned",
    )
    api.init_app(app)

    response = client.get(
        "/persons/{}/relationships/computers-owned".format(person.person_id),
        content_type="application/vnd.api+json",
    )
    assert response.status_code == 200, response.json["errors"]
