import marshmallow
import marshmallow_jsonapi
import requests

from .base import ExceptionConverter


class MarshmallowValidationErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, marshmallow.ValidationError):
            raise ValueError()

        retv = []
        messages = exc.normalized_messages()

        if "errors" in messages:
            retv = messages["errors"]

        for field, messages_list in messages.items():
            if field != "errors":
                retv.append(
                    {
                        "detail": messages_list,
                        "source": {"pointer": f"/data/attributes/{field}"},
                    }
                )

        for _ in retv:
            _["title"] = _.get("title", "ValidationError")
            _["http_status"] = requests.codes["unprocessable"]

        return retv


class MarshmallowJsonapiIncorrectTypeErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, marshmallow_jsonapi.exceptions.IncorrectTypeError):
            raise ValueError()

        return dict(
            title="IncorrectTypeError",
            detail=exc.detail,
            source={"pointer": exc.pointer},
            http_status=requests.codes["conflict"],
        )


MarshmallowJsonapiIncorrectTypeErrorConverter.register()
MarshmallowValidationErrorConverter.register()
