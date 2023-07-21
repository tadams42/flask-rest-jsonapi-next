import abc
from typing import List, Union

import flask

_CONVERTERS_REGISTRY = []
_REGISTRY_INTERNALS_ORDER = [
    "_FlaskRestJsonApiExceptionConverter",
    "_MarshmallowJsonapiIncorrectTypeErrorConverter",
    "_MarshmallowValidationErrorConverter",
    "_IntegrityErrorConverter",
    "_ArgumentErrorConverter",
    "_DataErrorConverter",
    "_InvalidRequestErrorConverter",
    "_MultipleResultsFoundConverter",
    "_NoResultFoundConverter",
    "_SQLProgrammingErrorConverter",
    "_SQLStatementErrorConverter",
    "_WerkzeugHttpErrorConverter",
]


class ConvertersRegistry:
    @classmethod
    def register(cls, klass):
        if klass and klass not in _CONVERTERS_REGISTRY:
            _CONVERTERS_REGISTRY.append(klass)

        cls._sort()

    @classmethod
    def _sort(cls):
        def _key(klass):
            if klass.__name__ in _REGISTRY_INTERNALS_ORDER:
                return _REGISTRY_INTERNALS_ORDER.index(klass.__name__)

            if klass.__name__ == "_GenericSQLAlchemyErrorConverter":
                return len(_REGISTRY_INTERNALS_ORDER) + 10

            if klass.__name__ == "_GenericErrorConverter":
                return len(_REGISTRY_INTERNALS_ORDER) + 20

            return len(_REGISTRY_INTERNALS_ORDER) + 1

        global _CONVERTERS_REGISTRY

        _CONVERTERS_REGISTRY = list(sorted(_CONVERTERS_REGISTRY, key=_key))


def convert(error: Union[int, Exception]) -> Union[List[dict], dict]:
    from .sqlalchemy import _GenericSQLAlchemyErrorConverter

    data = None

    for klass in _CONVERTERS_REGISTRY:
        try:
            data = klass.convert(error)
        except ValueError:
            pass

        if data:
            break

    return data


class ExceptionConverter(abc.ABC):
    def __init_subclass__(cls, *args, **kwargs):
        super().__init_subclass__(*args, **kwargs)
        ConvertersRegistry.register(cls)

    @abc.abstractclassmethod
    def convert(cls, exc: Exception) -> Union[List[dict], dict]:
        raise NotImplementedError()

    @classmethod
    def register(cls):
        # exists only for backward compatibility reasons
        # no-op because __init_subclass__ does the work
        pass


class _GenericErrorConverter(ExceptionConverter):
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
                    it nice and report the issue (together with complete contents of
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
