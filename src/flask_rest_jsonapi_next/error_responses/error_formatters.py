from typing import List, Optional, Union

import flask
import requests

from .exception_converters import convert

JSONAPI_RESPONSE_HEADERS = {"Content-Type": "application/vnd.api+json"}


def error_response_from(
    error: Union[int, Exception], request_id: str
) -> flask.Response:
    return _error_response(data=convert(error), request_id=request_id)


def error_response(
    title: str,
    detail: str,
    http_status: Union[str, int],
    request_id: str,
    code: Optional[Union[str, int]] = None,
    meta: Optional[dict] = None,
    source: Optional[str] = None,
) -> flask.Response:
    return _error_response(
        {
            "title": title,
            "detail": detail,
            "http_status": http_status,
            "code": code,
            "meta": meta,
            "source": source,
        },
        request_id=request_id,
    )


def _error_response(data: Union[List[dict], dict], request_id: str) -> flask.Response:
    body = {"jsonapi": {"version": "1.0"}}

    if isinstance(data, list):
        if request_id:
            for _ in data:
                _["request_id"] = request_id
        body["errors"] = [_normalize_single_error(**_) for _ in data]
    else:
        if request_id:
            data["request_id"] = request_id
        body["errors"] = [_normalize_single_error(**data)]

    if not request_id:
        for idx, _ in enumerate(body["errors"]):
            _["id"] = str(idx)

    status_code = next(iter(body["errors"]), dict()).get("status", requests.codes["✗"])

    return flask.make_response(
        flask.json.dumps(body), status_code, JSONAPI_RESPONSE_HEADERS
    )


def _normalize_single_error(
    title: str,
    detail: Union[List[str], str],
    http_status: Union[str, int],
    request_id: Optional[str] = None,
    code: Optional[Union[str, int]] = None,
    meta: Optional[dict] = None,
    source: Optional[str] = None,
) -> dict:
    error = {
        "status": str(http_status or requests.codes["✗"]),
        "title": str(title),
        "detail": [str(_) for _ in detail] if isinstance(detail, list) else str(detail),
    }

    if request_id:
        error["id"] = request_id

    if meta:
        error["meta"] = meta

    if code is not None:
        error["code"] = str(code)

    if source:
        error["source"] = source

    return error
