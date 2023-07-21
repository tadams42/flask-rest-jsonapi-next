import flask
import requests
import sqlalchemy
from sqlalchemy import orm

from .base import ExceptionConverter

_PSYCOPG = None

try:
    # Actually psycopg v3.x
    import psycopg

    _PSYCOPG = psycopg
except ImportError:
    pass


if not _PSYCOPG:
    try:
        # Actually psycopg v2.x
        import psycopg2

        _PSYCOPG = psycopg2
    except ImportError:
        pass


class _ArgumentErrorConverter(ExceptionConverter):
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


class _NoResultFoundConverter(ExceptionConverter):
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


class _MultipleResultsFoundConverter(ExceptionConverter):
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


class _UniqueViolationConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, _PSYCOPG.errors.UniqueViolation):
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


class _CheckViolationConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, _PSYCOPG.errors.CheckViolation):
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


class _ForeignKeyViolationConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, _PSYCOPG.errors.ForeignKeyViolation):
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


class _NotNullViolationConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, _PSYCOPG.errors.NotNullViolation):
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


class _UndefinedFunction(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, _PSYCOPG.errors.UndefinedFunction):
            raise ValueError()

        detail = ""
        diag = getattr(exc, "diag", None)
        if diag:
            detail = f"{diag.message_primary} ({diag.message_hint})"

        title = "SQLUndefinedFunction"
        http_status = requests.codes["server_error"]

        meta = dict()
        if "operator does not exist" in detail:
            # meta = {"sql_msg": detail}
            detail = (
                "SQL query couldn't coerce query parameter into type of table "
                "column. For example, it expected integer ({'user_id': 42}), but "
                "got string instead ({'user_id': '42'}). Check your filter "
                "expressions."
            )
            title = "SQLTypeError"
            http_status = requests.codes["unprocessable"]

        return dict(title=title, detail=detail, http_status=http_status, meta=meta)


class _IntegrityErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, sqlalchemy.exc.IntegrityError):
            raise ValueError()

        orig = getattr(exc, "orig", None)

        if _PSYCOPG:
            if isinstance(orig, _PSYCOPG.errors.UniqueViolation):
                retv = _UniqueViolationConverter.convert(orig)

            elif isinstance(orig, _PSYCOPG.errors.CheckViolation):
                retv = _CheckViolationConverter.convert(orig)

            elif isinstance(orig, _PSYCOPG.errors.ForeignKeyViolation):
                retv = _ForeignKeyViolationConverter.convert(orig)

            elif isinstance(orig, _PSYCOPG.errors.NotNullViolation):
                retv = _NotNullViolationConverter.convert(orig)

            elif isinstance(orig, _PSYCOPG.errors.UndefinedFunction):
                retv = _UndefinedFunction.convert(orig)

            else:
                raise ValueError()

        else:
            raise ValueError()

        if flask.current_app.debug:
            retv["meta"] = retv.get("meta", dict())
            retv["meta"]["exc"] = str(exc)

        return retv


class _InvalidRequestErrorConverter(ExceptionConverter):
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


class _DataErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, sqlalchemy.exc.DataError):
            raise ValueError()

        if hasattr(exc, "orig"):
            orig = exc.orig
            detail = None

            if hasattr(orig, "diag"):
                diag = orig.diag
                detail = getattr(diag, "message_primary", None)

            detail = (
                detail
                or f"Datastore error not caught by validation: {';'.join(_.strip() for _ in exc.orig.args)}"
            )

            return dict(
                title="DataError",
                detail=detail,
                http_status=requests.codes["unprocessable"],
                source={"pointer": "body"},
            )

        raise ValueError()


class _SQLProgrammingErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, sqlalchemy.exc.ProgrammingError):
            raise ValueError()

        orig = getattr(exc, "orig", None)

        if _PSYCOPG:
            if isinstance(orig, _PSYCOPG.errors.UndefinedFunction):
                retv = _UndefinedFunction.convert(orig)
                params = getattr(exc, "params", None)
                if params:
                    if "meta" not in retv:
                        retv["meta"] = dict()
                    retv["meta"]["sql_params"] = params
                return retv

        detail = ""
        if orig:
            detail = ";".join(orig.args)
        else:
            detail = ";".join(exc.args)

        return dict(
            title="SQLProgrammingError",
            detail=detail,
            http_status=requests.codes["server_error"],
            source={"pointer": "SQL"},
        )


class _SQLStatementErrorConverter(ExceptionConverter):
    @classmethod
    def convert(cls, exc):
        if not isinstance(exc, sqlalchemy.exc.StatementError):
            raise ValueError()

        detail = ""

        if hasattr(exc, "orig"):
            detail = ";".join(exc.orig.args)
        else:
            detail = ";".join(exc.args)

        return dict(
            title="SQLStatementError",
            detail=detail,
            http_status=requests.codes["unprocessable"],
            source={"pointer": "filter"},
        )


class _GenericSQLAlchemyErrorConverter(ExceptionConverter):
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
