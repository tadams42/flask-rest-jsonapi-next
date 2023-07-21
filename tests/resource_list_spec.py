from urllib.parse import urlencode

from flask import json


def test_get_list(client, api_middleware, person, person_2):
    with client:
        querystring = urlencode(
            {
                "page[number]": 1,
                "page[size]": 1,
                "fields[person]": "name,birth_date",
                "sort": "-name",
                "include": "computers.owner",
                "filter": json.dumps(
                    [
                        {
                            "and": [
                                {
                                    "name": "computers",
                                    "op": "any",
                                    "val": {
                                        "name": "serial",
                                        "op": "eq",
                                        "val": "0000",
                                    },
                                },
                                {
                                    "or": [
                                        {"name": "name", "op": "like", "val": "%test%"},
                                        {
                                            "name": "name",
                                            "op": "like",
                                            "val": "%test2%",
                                        },
                                    ]
                                },
                            ]
                        }
                    ]
                ),
            }
        )
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 200, response.json["errors"]


def test_get_list_with_simple_filter(client, api_middleware, person, person_2):
    with client:
        querystring = urlencode(
            {
                "page[number]": 1,
                "page[size]": 1,
                "fields[person]": "name,birth_date",
                "sort": "-name",
                "filter[name]": "test",
            }
        )
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 200, response.json["errors"]


def test_get_list_disable_pagination(client, api_middleware):
    with client:
        querystring = urlencode({"page[size]": 0})
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 200, response.json["errors"]


def test_head_list(client, api_middleware):
    with client:
        response = client.head("/persons", content_type="application/vnd.api+json")
        assert response.status_code == 200, response.json["errors"]


def test_post_list(client, api_middleware, computer):
    payload = {
        "data": {
            "type": "person",
            "attributes": {"name": "test"},
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.post(
            "/persons",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 201, response.json["errors"]


def test_post_list_nested_no_join(client, api_middleware, computer):
    payload = {
        "data": {
            "type": "string_json_attribute_person",
            "attributes": {
                "name": "test_name",
                "address": {
                    "street": "test_street",
                    "city": "test_city",
                    "state": "NC",
                    "zip": "00000",
                },
            },
        }
    }
    with client:
        response = client.post(
            "/string_json_attribute_persons",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        print(response.get_data())
        assert response.status_code == 201, response.json["errors"]
        assert (
            json.loads(response.get_data())["data"]["attributes"]["address"]["street"]
            == "test_street"
        )


def test_post_list_nested(client, api_middleware, computer):
    payload = {
        "data": {
            "type": "person",
            "attributes": {
                "name": "test",
                "tags": [{"key": "k1", "value": "v1"}, {"key": "k2", "value": "v2"}],
            },
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.post(
            "/persons",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 201, response.json["errors"]
        assert (
            json.loads(response.get_data())["data"]["attributes"]["tags"][0]["key"]
            == "k1"
        )


def test_post_list_single(client, api_middleware, person):
    payload = {
        "data": {
            "type": "computer",
            "attributes": {"serial": "1"},
            "relationships": {
                "owner": {"data": {"type": "person", "id": str(person.person_id)}}
            },
        }
    }

    with client:
        response = client.post(
            "/computers",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 201, response.json["errors"]


def test_get_list_response(client, api_middleware):
    with client:
        response = client.get(
            "/persons_response", content_type="application/vnd.api+json"
        )
        assert response.status_code == 200, response.json["errors"]


def test_get_list_jsonapiexception(client, api_middleware):
    with client:
        response = client.get(
            "/persons_jsonapiexception", content_type="application/vnd.api+json"
        )
        assert response.status_code == 500, response.json["errors"]


def test_get_list_exception(client, api_middleware):
    with client:
        response = client.get(
            "/persons_exception", content_type="application/vnd.api+json"
        )
        assert response.status_code == 500, response.json["errors"]


def test_get_list_without_schema(client, api_middleware):
    with client:
        response = client.post(
            "/persons_without_schema", content_type="application/vnd.api+json"
        )
        assert response.status_code == 500, response.json["errors"]


def test_get_list_bad_request(client, api_middleware):
    with client:
        querystring = urlencode({"page[number": 3})
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_invalid_fields(client, api_middleware):
    with client:
        querystring = urlencode({"fields[person]": "error"})
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_invalid_include(client, api_middleware):
    with client:
        querystring = urlencode({"include": "error"})
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_invalid_filters_parsing(client, api_middleware):
    with client:
        querystring = urlencode({"filter": "error"})
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_invalid_page(client, api_middleware):
    with client:
        querystring = urlencode({"page[number]": "error"})
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_invalid_sort(client, api_middleware):
    with client:
        querystring = urlencode({"sort": "error"})
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_invalid_filters_val(client, api_middleware):
    with client:
        querystring = urlencode(
            {"filter": json.dumps([{"name": "computers", "op": "any"}])}
        )
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_name(client, api_middleware):
    with client:
        querystring = urlencode(
            {
                "filter": json.dumps(
                    [{"name": "computers__serial", "op": "any", "val": "1"}]
                )
            }
        )
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 200, response.json["errors"]


def test_get_list_no_name(client, api_middleware):
    with client:
        querystring = urlencode({"filter": json.dumps([{"op": "any", "val": "1"}])})
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_no_op(client, api_middleware):
    with client:
        querystring = urlencode(
            {"filter": json.dumps([{"name": "computers__serial", "val": "1"}])}
        )
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_attr_error(client, api_middleware):
    with client:
        querystring = urlencode(
            {"filter": json.dumps([{"name": "error", "op": "eq", "val": "1"}])}
        )
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_get_list_field_error(client, api_middleware):
    with client:
        querystring = urlencode(
            {"filter": json.dumps([{"name": "name", "op": "eq", "field": "error"}])}
        )
        response = client.get(
            "/persons" + "?" + querystring, content_type="application/vnd.api+json"
        )
        assert response.status_code == 400, response.json["errors"]


def test_post_list_incorrect_type(client, api_middleware, computer):
    payload = {
        "data": {
            "type": "error",
            "attributes": {"name": "test"},
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.post(
            "/persons",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 409, response.json["errors"]


def test_post_list_validation_error(client, api_middleware, computer):
    payload = {
        "data": {
            "type": "person",
            "attributes": {},
            "relationships": {
                "computers": {"data": [{"type": "computer", "id": str(computer.id)}]}
            },
        }
    }

    with client:
        response = client.post(
            "/persons",
            data=json.dumps(payload),
            content_type="application/vnd.api+json",
        )
        assert response.status_code == 422, response.json["errors"]
