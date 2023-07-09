import pytest
from flask import json

from flask_rest_jsonapi_next import ResourceDetail


def test_get_detail(client, api_middleware, person):
    with client:
        response = client.get(
            "/persons/" + str(person.person_id), content_type="application/vnd.api+json"
        )
        assert response.status_code == 200, response.json["errors"]


def test_patch_detail(client, api_middleware, computer, person):
    payload = {
        "data": {
            "id": str(person.person_id),
            "type": "person",
            "attributes": {"name": "test2"},
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.patch(
            "/persons/" + str(person.person_id),
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_patch_detail_nested(client, api_middleware, computer, person):
    payload = {
        "data": {
            "id": str(person.person_id),
            "type": "person",
            "attributes": {
                "name": "test2",
                "tags": [{"key": "new_key", "value": "new_value"}],
                "single_tag": {"key": "new_single_key", "value": "new_single_value"},
            },
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.patch(
            "/persons/" + str(person.person_id),
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]
        response_dict = json.loads(response.get_data())
        assert response_dict["data"]["attributes"]["tags"][0]["key"] == "new_key"
        assert (
            response_dict["data"]["attributes"]["single_tag"]["key"] == "new_single_key"
        )


def test_delete_detail(client, api_middleware, person):
    with client:
        response = client.delete(
            "/persons/" + str(person.person_id), content_type="application/vnd.api+json"
        )
        assert response.status_code == 200, response.json["errors"]


def test_get_relationship(db, client, api_middleware, computer, person):
    person.computers = [computer]
    db.session.commit()

    with client:
        response = client.get(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_get_relationship_empty(client, api_middleware, person):
    with client:
        response = client.get(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_get_relationship_single(db, client, api_middleware, computer, person):
    computer.person = person
    db.session.commit()

    with client:
        response = client.get(
            "/computers/" + str(computer.id) + "/relationships/owner",
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_get_relationship_single_empty(db, client, api_middleware, computer):
    with client:
        response = client.get(
            "/computers/" + str(computer.id) + "/relationships/owner",
            content_type="application/vnd.api+json",
        )
        response_json = json.loads(response.get_data())
        assert None is response_json["data"]
        assert response.status_code == 200, response.json["errors"]


def test_issue_49(db, client, api_middleware, person, person_2):
    with client:
        for p in [person, person_2]:
            response = client.get(
                "/persons/"
                + str(p.person_id)
                + "/relationships/computers?include=computers",
                content_type="application/vnd.api+json",
            )
            assert response.status_code == 200, response.json["errors"]
            assert (json.loads(response.get_data()))["links"][
                "related"
            ] == "/persons/" + str(p.person_id) + "/computers"


def test_post_relationship(client, api_middleware, computer, person):
    payload = {"data": [{"type": "computer", "id": str(computer.id)}]}

    with client:
        response = client.post(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_post_relationship_not_list(client, api_middleware, computer, person):
    payload = {"data": {"type": "person", "id": str(person.person_id)}}

    with client:
        response = client.post(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_patch_relationship(client, api_middleware, computer, person):
    payload = {"data": [{"type": "computer", "id": str(computer.id)}]}

    with client:
        response = client.patch(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_patch_relationship_single(client, api_middleware, computer, person):
    payload = {"data": {"type": "person", "id": str(person.person_id)}}
    with client:
        response = client.patch(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_delete_relationship(db, client, api_middleware, computer, person):
    person.computers = [computer]
    db.session.commit()

    payload = {"data": [{"type": "computer", "id": str(computer.id)}]}

    with client:
        response = client.delete(
            "/persons/"
            + str(person.person_id)
            + "/relationships/computers?include=computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_delete_relationship_single(db, client, api_middleware, computer, person):
    computer.person = person
    db.session.commit()

    payload = {"data": {"type": "person", "id": str(person.person_id)}}

    with client:
        response = client.delete(
            "/computers/" + str(computer.id) + "/relationships/owner",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 200, response.json["errors"]


def test_patch_detail_incorrect_type(client, api_middleware, computer, person):
    payload = {
        "data": {
            "id": str(person.person_id),
            "type": "error",
            "attributes": {"name": "test2"},
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.patch(
            "/persons/" + str(person.person_id),
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 409, response.json["errors"]


def test_patch_detail_validation_error(client, api_middleware, computer, person):
    payload = {
        "data": {
            "id": str(person.person_id),
            "type": "person",
            "attributes": {"name": {"test2": "error"}},
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.patch(
            "/persons/" + str(person.person_id),
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 422, response.json["errors"]


def test_patch_detail_missing_id(client, api_middleware, computer, person):
    payload = {
        "data": {
            "type": "person",
            "attributes": {"name": "test2"},
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.patch(
            "/persons/" + str(person.person_id),
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 400, response.json["errors"]


def test_patch_detail_wrong_id(client, api_middleware, computer, person):
    payload = {
        "data": {
            "id": "error",
            "type": "person",
            "attributes": {"name": "test2"},
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.patch(
            "/persons/" + str(person.person_id),
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 422, response.json["errors"]


def test_get_detail_object_not_found(client, api_middleware):
    with client:
        response = client.get("/persons/3", content_type="application/vnd.api+json")
        assert response.status_code == 404, response.json["errors"]


def test_detail_wrong_data_layer_kwargs_type():
    with pytest.raises(Exception):

        class PersonDetail(ResourceDetail):
            data_layer = list()

        PersonDetail()


def test_detail_wrong_data_layer_inheritance(wrong_data_layer):
    with pytest.raises(Exception):

        class PersonDetail(ResourceDetail):
            data_layer = {"class": wrong_data_layer}

        PersonDetail()
