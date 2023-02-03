import logging
from typing import Callable, Optional, Type, Union

import flask
from werkzeug.exceptions import default_exceptions

from .error_formatters import error_response_from

logger = logging.getLogger(__name__)


class ErrorsAsJsonApi:
    """
    Middleware implements part of JSON:API concerning error responses (
    https://jsonapi.org/format/1.1/#error-objects)

    - installs exception handler to Flask app which returns all unhandled exceptions as
      JSON:API formatted errors
    - implements formatters for various exception types
    - implements generic formatter for any new and unknown exception types

    Influenced by: https://coderwall.com/p/xq88zg/json-exception-handler-for-flask
    """

    def __init__(self, app: Optional[flask.Flask] = None):
        if app:
            self.init_app(app)

    def init_app(self, app: flask.Flask):
        self.register(Exception, app=app)
        for http_status in default_exceptions:
            self.register(http_status, app=app)

    @classmethod
    def register(
        cls,
        exception_or_code: Union[int, Type[Exception]],
        handler: Optional[Callable] = None,
        app: Optional[flask.Flask] = None,
    ):
        """
        Registers custom handler for exception or HTTP status code:

        .. code-block:: python

            json_error_response = ErrorsAsJsonApi(app)
            def zero_division_handler(error):
                return flask.jsonify({"message": "Don't divide by zero!!!!!"})
            json_error_response.register(
                ZeroDivisionError, handler=zero_division_handler
            )
        """
        (app or flask.current_app).register_error_handler(
            exception_or_code, handler or cls._std_handler
        )

    @classmethod
    def _std_handler(cls, error):
        if error in {401, 403, 405} or isinstance(
            error,
            (default_exceptions[401], default_exceptions[403], default_exceptions[405]),
        ):
            logger.debug(
                "Exception bubbled to top level handler and was returned as HTTP "
                "JSON response.",
                exc_info=True,
            )
        else:
            logger.error(
                "Exception bubbled to top level handler and was returned as HTTP "
                "JSON response.",
                exc_info=True,
            )

        return error_response_from(
            error,
            getattr(getattr(flask, "g", None), "request_id", ""),
        )
