import pytest
import sqlalchemy.exc
from flask_rest_jsonapi_next.error_responses.exception_converters.base import convert

psycopg_errors = pytest.importorskip("psycopg.errors", reason="psycopg not installed")


def _make_operational_error(orig):
    return sqlalchemy.exc.OperationalError(
        statement="SELECT 1",
        params={},
        orig=orig,
    )


class DescribeOperationalErrorConverter:
    def it_returns_503_for_AdminShutdown(self, app):
        orig = psycopg_errors.AdminShutdown(
            "terminating connection due to administrator command"
        )
        result = convert(_make_operational_error(orig))
        assert result["http_status"] == 503
        assert result["title"] == "DatabaseTemporarilyUnavailable"

    def it_returns_503_for_CrashShutdown(self, app):
        orig = psycopg_errors.CrashShutdown("terminating connection due to crash")
        result = convert(_make_operational_error(orig))
        assert result["http_status"] == 503

    def it_returns_503_for_CannotConnectNow(self, app):
        orig = psycopg_errors.CannotConnectNow("database is starting up")
        result = convert(_make_operational_error(orig))
        assert result["http_status"] == 503

    def it_does_not_intercept_other_OperationalErrors(self, app):
        orig = psycopg_errors.ConnectionFailure("connection failed")
        result = convert(_make_operational_error(orig))
        assert result["http_status"] != 503
