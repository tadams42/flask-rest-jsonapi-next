_HAS_PSYCOPG2 = False
try:
    import psycopg2

    _HAS_PSYCOPG2 = True
except ImportError:
    pass

CONVERTERS_REGISTRY = []


class ConvertersRegistry:
    @classmethod
    def register(cls, klass):
        if not CONVERTERS_REGISTRY:
            from . import flask_rest_jsonapi, marshamallow, sqlalchemy, werkzeug

            # Order is important!
            CONVERTERS_REGISTRY.extend(
                [
                    flask_rest_jsonapi.FlaskRestJsonApiExceptionConverter,
                    marshamallow.MarshmallowJsonapiIncorrectTypeErrorConverter,
                    marshamallow.MarshmallowValidationErrorConverter,
                ]
            )

            if _HAS_PSYCOPG2:
                CONVERTERS_REGISTRY.append(sqlalchemy.IntegrityErrorConverter)

            CONVERTERS_REGISTRY.extend(
                [
                    sqlalchemy.ArgumentErrorConverter,
                    sqlalchemy.DataErrorConverter,
                    sqlalchemy.InvalidRequestErrorConverter,
                    sqlalchemy.MultipleResultsFoundConverter,
                    sqlalchemy.NoResultFoundConverter,
                    sqlalchemy.SQLStatementErrorConverter,
                ]
            )

            CONVERTERS_REGISTRY.append(werkzeug.WerkzeugHttpErrorConverter)

        if klass and klass not in CONVERTERS_REGISTRY:
            CONVERTERS_REGISTRY.append(klass)

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


ConvertersRegistry.register(None)
