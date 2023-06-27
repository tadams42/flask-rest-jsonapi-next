from typing import List, Union

from . import flask_rest_jsonapi, marshamallow, sqlalchemy, werkzeug
from .registry import ConvertersRegistry


def convert(error: Union[int, Exception]) -> Union[List[dict], dict]:
    return ConvertersRegistry.get_converted_data(error)


__all__ = ["convert"]
