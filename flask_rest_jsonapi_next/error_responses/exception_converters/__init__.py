from typing import List, Union

from . import flask_rest_jsonapi, marshamallow, sqlalchemy, werkzeug
from .base import CONVERTERS_REGISTRY, GenericErrorConverter


def convert(error: Union[int, Exception]) -> Union[List[dict], dict]:
    data = None

    for klass in CONVERTERS_REGISTRY:
        try:
            data = klass.convert(error)
        except ValueError:
            pass

        if data:
            break

    if not data:
        data = GenericErrorConverter.convert(error)

    return data


__all__ = ["convert"]
