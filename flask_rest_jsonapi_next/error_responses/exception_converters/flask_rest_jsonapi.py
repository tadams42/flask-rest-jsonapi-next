from ...exceptions import JsonApiException
from .base import ExceptionConverter


class FlaskRestJsonApiExceptionConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, JsonApiException):
            raise ValueError()

        retv = dict(title=exc.title, detail=exc.detail, http_status=exc.status)

        if exc.source:
            retv["source"] = exc.source

        if exc.meta:
            retv["meta"] = exc.meta

        return retv


FlaskRestJsonApiExceptionConverter.register()
