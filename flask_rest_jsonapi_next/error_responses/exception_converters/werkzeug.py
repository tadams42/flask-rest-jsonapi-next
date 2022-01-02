import werkzeug

from .base import ExceptionConverter


class WerkzeugHttpErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, werkzeug.exceptions.HTTPException):
            raise ValueError()

        return dict(title=exc.name, detail=exc.description, http_status=exc.code)


WerkzeugHttpErrorConverter.register()
