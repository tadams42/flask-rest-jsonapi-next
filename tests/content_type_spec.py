from flask import json


# test various Accept headers
def test_single_accept_header(client, api_middleware):
    with client:
        response = client.get(
            "/persons",
            content_type="application/vnd.api+json",
            headers={"Accept": "application/vnd.api+json"},
        )
        assert response.status_code == 200, response.json["errors"]


def test_multiple_accept_header(client, api_middleware):
    with client:
        response = client.get(
            "/persons",
            content_type="application/vnd.api+json",
            headers={
                "Accept": "*/*, application/vnd.api+json, application/vnd.api+json;q=0.9"
            },
        )
        assert response.status_code == 200, response.json["errors"]


def test_wrong_accept_header(client, api_middleware):
    with client:
        response = client.get(
            "/persons",
            content_type="application/vnd.api+json",
            headers={
                "Accept": "application/vnd.api+json;q=0.7, application/vnd.api+json;q=0.9"
            },
        )
        assert response.status_code == 406, response.json["errors"]


# test Content-Type error
def test_wrong_content_type(client, api_middleware):
    payload = {"data": {"type": "person", "attributes": {"name": "test"}}}
    with client:
        response = client.post(
            "/persons", data=json.dumps(payload), content_type="foobar"
        )
        assert response.status_code == 415, response.json


def test_ok_content_type1(client, api_middleware, person):
    payload = {"data": {"type": "person", "attributes": {"name": "test"}}}
    with client:
        response = client.post(
            "/persons",
            data=json.dumps(payload),
            content_type="application/vnd.api+json;charset=UTF-8",
        )
        assert response.status_code == 201


def test_ok_content_type2(client, api_middleware, person):
    payload = {"data": {"type": "person", "attributes": {"name": "test"}}}
    with client:
        response = client.post(
            "/persons", data=json.dumps(payload), content_type="application/json"
        )
        assert response.status_code == 201
