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
        # Do we need this?
        # @app.after_request
        # def add_id_to_errors(response):
        #     if 400 <= response.status_code < 600 and response.is_json:
        #         data = response.json
        #         if (
        #             "errors" in data
        #             and len(data["errors"]) > 0
        #             and "id" not in data["errors"][0]
        #         ):
        #             data["errors"][0]["id"] = request_id()
        #             status_code = response.status_code
        #             response = flask.jsonify(data)
        #             response.status_code = status_code

        #     return response

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
        logger.error(
            "Exception bubbled to top level handler and was returned as HTTP "
            "JSON response.",
            exc_info=True,
        )
        return error_response_from(
            error,
            getattr(getattr(flask, "g", None), "request_id", "X-Request-ID Unknown"),
        )
