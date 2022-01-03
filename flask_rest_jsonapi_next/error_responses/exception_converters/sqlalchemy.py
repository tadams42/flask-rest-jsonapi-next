import flask
import requests
import sqlalchemy
from sqlalchemy import orm

_HAS_PSYCOPG2 = False
try:
    import psycopg2

    _HAS_PSYCOPG2 = True
except ImportError:
    pass

from .base import ExceptionConverter


class ArgumentErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, sqlalchemy.exc.ArgumentError):
            raise ValueError()

        return dict(
            title="SQLArgumentError",
            detail=(
                "Tried to generate SQL query with unknown attribute! Check your filter "
                "for typos and virtual attributes."
            ),
            http_status=requests.codes["unprocessable"],
            meta={"sql_exception": str(exc)} if flask.current_app.debug else None,
        )


ArgumentErrorConverter.register()


class NoResultFoundConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, orm.exc.NoResultFound):
            raise ValueError()

        return dict(
            title="SQLNoResultFound",
            detail="Object not found!",
            http_status=requests.codes["not_found"],
            meta={"sql_exception": str(exc)} if flask.current_app.debug else None,
        )


NoResultFoundConverter.register()


class MultipleResultsFoundConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, orm.exc.MultipleResultsFound):
            raise ValueError()

        return dict(
            title="SQLMulitpleResultsFound",
            detail="Query was supposed to return one, but many found!",
            http_status=requests.codes["unprocessable"],
            meta={"sql_exception": str(exc)} if flask.current_app.debug else None,
        )


MultipleResultsFoundConverter.register()


class UniqueViolationConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, psycopg2.errors.UniqueViolation):
            raise ValueError()

        return dict(
            title="SQLUniqueViolation",
            detail=(
                "Unique constraint violated! "
                + (getattr(getattr(exc, "diag", None), "message_detail", ""))
            ),
            http_status=requests.codes["conflict"],
            meta={"psql_exception": str(exc)} if flask.current_app.debug else None,
        )


if _HAS_PSYCOPG2:

    class CheckViolationConverter(ExceptionConverter):
        @classmethod
        def convert(cls, exc):
            if not isinstance(exc, psycopg2.errors.CheckViolation):
                raise ValueError()

            return dict(
                title="SQLCheckViolation",
                detail="SQL check constraint violated!",
                http_status=requests.codes["unprocessable"],
                meta={
                    "psql_exception": str(exc),
                    "psql_diag": f"{getattr(getattr(exc, 'diag', None), 'constraint_name', '')}",
                }
                if flask.current_app.debug
                else None,
            )

    CheckViolationConverter.register()

    class ForeignKeyViolationConverter(ExceptionConverter):
        @classmethod
        def convert(cls, exc):
            if not isinstance(exc, psycopg2.errors.ForeignKeyViolation):
                raise ValueError()

            return dict(
                title="SQLForeignKeyViolation",
                detail=(
                    "Referential integity violation! You most probably tried to "
                    "delete a parent object while there are still children "
                    "referencing it."
                ),
                http_status=requests.codes["unprocessable"],
                meta={
                    "psql_exception": str(exc),
                    "psql_diag": f"{getattr(getattr(exc, 'diag', None), 'constraint_name', '')}",
                }
                if flask.current_app.debug
                else None,
            )

    CheckViolationConverter.register()

    class NotNullViolationConverter(ExceptionConverter):
        @classmethod
        def convert(cls, exc):
            if not isinstance(exc, psycopg2.errors.NotNullViolation):
                raise ValueError()

            try:
                additional_details = exc.args[0].split("DETAIL")[0].strip()
            except Exception:
                additional_details = ""

            detail = "Not-null constraint violated!"
            if additional_details:
                detail = detail + f" ({additional_details})"

            return dict(
                title="SQLNotNullViolation",
                detail=detail,
                http_status=requests.codes["unprocessable"],
                meta={
                    "psql_exception": str(exc),
                    "psql_diag": f" [{getattr(getattr(exc, 'diag', None), 'message_primary', '')}]",
                }
                if flask.current_app.debug
                else None,
            )

    NotNullViolationConverter.register()

    class IntegrityErrorConverter(ExceptionConverter):
        @classmethod
        def convert(cls, exc):
            if not isinstance(exc, sqlalchemy.exc.IntegrityError):
                raise ValueError()

            orig = getattr(exc, "orig", None)

            if isinstance(orig, psycopg2.errors.UniqueViolation):
                retv = UniqueViolationConverter.convert(orig)

            elif isinstance(orig, psycopg2.errors.CheckViolation):
                retv = CheckViolationConverter.convert(orig)

            elif isinstance(orig, psycopg2.errors.ForeignKeyViolation):
                retv = ForeignKeyViolationConverter.convert(orig)

            elif isinstance(orig, psycopg2.errors.NotNullViolation):
                retv = NotNullViolationConverter.convert(orig)

            else:
                raise ValueError()

            if flask.current_app.debug:
                retv["meta"] = retv.get("meta", dict())
                retv["meta"]["exc"] = str(exc)

            return retv

    IntegrityErrorConverter.register()


class InvalidRequestErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, sqlalchemy.exc.InvalidRequestError):
            raise ValueError()

        if "'any()' not implemented for scalar attributes. Use has()." in exc.args:
            return dict(
                title="InvalidFilters",
                detail="Invalid filters querystring parameter: for fileds on relations use `has`, not `any`.",
                http_status=requests.codes["unprocessable"],
                source={"parameter": "filter"},
            )

        raise ValueError()


class DataErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, sqlalchemy.exc.DataError):
            raise ValueError()

        if hasattr(exc, "orig"):
            return dict(
                title="DataError",
                detail=f"Datastore error not caught by validation: {';'.join(_.strip() for _ in exc.orig.args)}",
                http_status=requests.codes["unprocessable"],
                source={"pointer": "body"},
            )

        raise ValueError()


class SQLAlchemyErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, sqlalchemy.exc.SQLAlchemyError):
            raise ValueError()

        meta = {}
        if flask.current_app.debug:
            meta = {"exception": str(exc)}
            orig = getattr(exc, "orig", None)
            if orig:
                meta["driver_exception"] = str(orig)

        return dict(
            title=type(exc).__name__,
            detail="Unexpected database error caused by either a backend bug or infrastructure outages.",
            http_status=requests.codes["✗"],
            meta=meta,
        )
