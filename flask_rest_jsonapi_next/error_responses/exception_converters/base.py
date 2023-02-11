import abc
from typing import List, Union

import flask
import sqlalchemy

CONVERTERS_REGISTRY = set()


class ConvertersRegistry:
    @classmethod
    def register(cls, klass):
        CONVERTERS_REGISTRY.add(klass)

    @classmethod
    def get_converted_data(cls, err):
        from .sqlalchemy import GenericSQLAlchemyErrorConverter

        data = None

        for klass in CONVERTERS_REGISTRY:
            try:
                data = klass.convert(err)
            except ValueError:
                pass

            if data:
                break

        if not data:
            try:
                data = GenericSQLAlchemyErrorConverter.convert(err)
            except ValueError:
                pass

        if not data:
            data = GenericErrorConverter.convert(err)

        return data


class ExceptionConverter(abc.ABC):
    @abc.abstractclassmethod
    def convert(cls, exc: Exception) -> Union[List[dict], dict]:
        raise NotImplementedError()

    @classmethod
    def register(cls):
        ConvertersRegistry.register(cls)


class GenericErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        title = type(exc).__name__
        http_status = detail = meta = None

        if hasattr(exc, "message") and exc.message:
            detail = exc.message
        elif hasattr(exc, "description") and exc.description:
            detail = exc.description
        if not detail:
            if flask.current_app.debug:
                detail = str(exc)
            else:
                detail = """
                    ************************** Congratulations!!!! **************************
                    You have just discovered new, unknown species of backend bug! Play
                    it nice and report the issue (together with complete contenets of
                    this error response) to backend maintainers."
                """

        meta = {}
        if hasattr(exc, "payload") and exc.payload:
            meta = {"payload": exc.payload}
        elif hasattr(exc, "response") and exc.response:
            meta = {"payload": exc.response}

        http_status = http_status or 500
        if isinstance(exc, (ValueError, KeyError)):
            http_status = 400
        elif hasattr(exc, "code") and exc.code is not None:
            http_status = exc.code
        elif hasattr(exc, "status_code") and exc.status_code is not None:
            http_status = exc.status_code

        try:
            http_status = int(http_status)
        except ValueError:
            http_status = 500

        calculated_code = int(http_status / 100) * 100
        if calculated_code == 400:
            meta["errors_data"] = str(exc)

        retv = dict(title=title, detail=detail, http_status=http_status)
        if meta:
            retv["meta"] = meta

        return retv
