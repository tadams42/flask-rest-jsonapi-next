# CLAUDE.md

This is a Python Flask extension library implementing JSON:API specification.

## Python tooling and development environment

Project is using `uv` for managing Python versions, virtual environments and all other
Python tooling. `uv` command is available as system-wide utility, you don't need to
install it.

Project is using virtual environment in `./.venv/`. This environment is already set up
and correctly configured.

Do NOT use `source .venv/bin/activate`; invoke tools via `.venv/bin/<tool>` or simply by
`uv run <tool>`.

## Commands

```sh
uv sync --active # Install dependencies

# Run full test suite
uv run pytest

# Run a single test file
uv run pytest tests/sqlalchemy_data_layer_spec.py

# Run a single test by name
uv run pytest tests/sqlalchemy_data_layer_spec.py::DescribeAlchemy::it_creates_object

# Lint
uv run ruff check .

# Format
uv run ruff format .
```

## Architecture

The core abstraction is: **Resource classes** handle HTTP and JSON:API protocol concerns; **Data Layer classes** handle persistence.

### Request flow

1. Flask routes to a `ResourceList`, `ResourceDetail`, or `ResourceRelationship` (all extend Flask's `MethodView`)
2. `dispatch_request()` runs `check_headers`, then delegates to the HTTP method handler
3. The method handler calls lifecycle hooks (`before_*`), then calls the configured data layer, then calls `after_*` hooks
4. Response is serialized via the configured marshmallow-jsonapi schema and wrapped in JSON:API envelope

### Resource configuration

```python
class PersonList(ResourceList):
    schema = PersonSchema          # marshmallow-jsonapi Schema subclass
    data_layer = {
        'session': db.session,
        'model': Person,
        # Optional overrides:
        # 'class': CustomDataLayer,
        # 'id_field': 'custom_id',   # model attribute for ID lookup
        # 'url_field': 'id',         # URL parameter name
        # 'eagerload_includes': True,
        # 'methods': {'before_create_object': fn, ...},
    }
```

Lifecycle hooks are defined as methods on the Resource class (`before_get`, `after_post`, etc.) or injected via `data_layer['methods']`.

### Data layers

`BaseDataLayer` (`data_layers/base.py`) defines the interface: `create_object`, `get_object`, `get_collection`, `update_object`, `delete_object`, plus relationship variants. All have `before_*`/`after_*` hook points.

`SqlalchemyDataLayer` (`data_layers/alchemy.py`) is the main implementation. Key non-obvious behaviors:
- Supports both SQLAlchemy 1.x (legacy `Query`) and 2.x (`select`)
- `apply_relationships(data, obj)` — attaches related SQLAlchemy objects from JSON:API relationship data
- `apply_nested_fields(data, obj)` — handles `Nested`/`List` schema fields mapped to JSON columns or nested relationships
- `eagerload_includes(query, qs)` — converts dot-notation include paths to SQLAlchemy `joinedload` chains to avoid N+1

### Filtering (`data_layers/filtering/alchemy.py`)

`create_filters(model, filter_info, resource)` builds SQLAlchemy filter expressions from JSON:API query params. The `Node` class recursively resolves filter trees, handles type coercion (int/date/Decimal), enum casting, and relationship traversal via dot notation (e.g., `filter[author.name][eq]=foo`).

Logical operators `or`, `and`, `not` produce nested filter trees.

### Schema integration (`schema.py`)

`compute_schema(schema_cls, defaults, qs, include)` applies sparse fieldsets (`fields[type]=...`) and wires up compound document includes. Schemas must be `marshmallow_jsonapi.Schema` subclasses with a `Meta` class defining `type_`, `self_view`, `self_view_kwargs`, `self_view_many`.

`get_relationships`, `get_nested_fields`, `get_model_field` are used by the data layer to know which schema fields require special handling during save/load.

### Exception hierarchy (`exceptions.py`)

`JsonApiException` is the base. Subclasses carry `status`, `title`, `detail`, `source`. `ErrorsAsJsonApi` (registered on the Flask app) catches these and formats them as JSON:API error responses. Invalid query params raise `InvalidFilters`, `InvalidField`, `InvalidSort`, `InvalidInclude`.

## Test conventions

Tests use BDD-style naming. Pytest is configured to discover:
- Classes: `Describe*`, `When*`
- Functions: `it_*`, `test_*`, `then_*`, `when_*`
- Files: `*_spec.py`, `*_test.py`, `test_*.py`

Test factories (models, schemas, Flask app) live in `tests/factories/`. The `conftest.py` provides the shared Flask app, SQLAlchemy session, and test client.
