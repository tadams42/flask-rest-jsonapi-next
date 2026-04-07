"""Tests for SqlalchemyDataLayer support of sa.Select (SQLAlchemy 2.x) query objects
alongside the legacy orm.Query interface.

Covers:
- _is_select() helper
- _exec_one(), _exec_all(), _exec_count() with both query types
- get_object() and get_collection() end-to-end when query() / retrieve_object_query()
  returns a sa.Select
- as_query=True is ignored when the underlying query is a sa.Select
"""

import pytest
import sqlalchemy

from flask_rest_jsonapi_next import SqlalchemyDataLayer
from flask_rest_jsonapi_next.data_layers.alchemy import _is_select
from flask_rest_jsonapi_next.querystring import QueryStringManager


# ---------------------------------------------------------------------------
# Helper subclasses that return sa.Select instead of orm.Query
# ---------------------------------------------------------------------------


class SelectRetrieveDataLayer(SqlalchemyDataLayer):
    """Overrides retrieve_object_query to return sa.Select."""

    def retrieve_object_query(self, view_kwargs, filter_field, filter_value):
        return sqlalchemy.select(self.model).where(filter_field == filter_value)


class SelectQueryDataLayer(SqlalchemyDataLayer):
    """Overrides query() to return sa.Select."""

    def query(self, view_kwargs):
        return sqlalchemy.select(self.model)


# ---------------------------------------------------------------------------
# _is_select
# ---------------------------------------------------------------------------


def test_is_select_returns_true_for_sa_select(person_model):
    assert _is_select(sqlalchemy.select(person_model)) is True


def test_is_select_returns_false_for_orm_query(db, person_model):
    assert _is_select(db.session.query(person_model)) is False


# ---------------------------------------------------------------------------
# _exec_one
# ---------------------------------------------------------------------------


def test_exec_one_with_orm_query_returns_object(db, person_model, person):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    query = db.session.query(person_model).filter(
        person_model.person_id == person.person_id
    )
    result = dl._exec_one(query)
    assert result.person_id == person.person_id


def test_exec_one_with_sa_select_returns_object(db, person_model, person):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    query = sqlalchemy.select(person_model).where(
        person_model.person_id == person.person_id
    )
    result = dl._exec_one(query)
    assert result.person_id == person.person_id


def test_exec_one_with_sa_select_raises_on_no_result(db, person_model):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    query = sqlalchemy.select(person_model).where(person_model.person_id == -1)
    with pytest.raises(Exception):
        dl._exec_one(query)


# ---------------------------------------------------------------------------
# _exec_all
# ---------------------------------------------------------------------------


def test_exec_all_with_orm_query_returns_list(db, person_model, person):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    result = dl._exec_all(db.session.query(person_model))
    assert isinstance(result, list)
    assert any(p.person_id == person.person_id for p in result)


def test_exec_all_with_sa_select_returns_list(db, person_model, person):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    result = dl._exec_all(sqlalchemy.select(person_model))
    assert isinstance(result, list)
    assert any(p.person_id == person.person_id for p in result)


# ---------------------------------------------------------------------------
# _exec_count
# ---------------------------------------------------------------------------


def test_exec_count_with_orm_query_returns_count(db, person_model, person):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    count = dl._exec_count(db.session.query(person_model))
    assert isinstance(count, int)
    assert count >= 1


def test_exec_count_with_sa_select_returns_count(db, person_model, person):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    count = dl._exec_count(sqlalchemy.select(person_model))
    assert isinstance(count, int)
    assert count >= 1


def test_exec_count_with_sa_select_returns_zero_for_empty_result(db, person_model):
    dl = SqlalchemyDataLayer(dict(session=db.session, model=person_model))
    count = dl._exec_count(
        sqlalchemy.select(person_model).where(person_model.person_id == -1)
    )
    assert count == 0


# ---------------------------------------------------------------------------
# get_object end-to-end with sa.Select from retrieve_object_query
# ---------------------------------------------------------------------------


def test_get_object_with_sa_select_retrieve_query(db, person_model, person_list, person):
    dl = SelectRetrieveDataLayer(
        dict(session=db.session, model=person_model, resource=person_list)
    )
    # url_field defaults to "id"; person_id is the PK resolved by get_object
    result = dl.get_object({"id": person.person_id})
    assert result.person_id == person.person_id


# ---------------------------------------------------------------------------
# get_collection end-to-end with sa.Select from query()
# ---------------------------------------------------------------------------


def test_get_collection_with_sa_select_query(
    db, person_model, person_list, person_schema, person, app
):
    app.config["PAGE_SIZE"] = 20
    with app.app_context():
        dl = SelectQueryDataLayer(
            dict(session=db.session, model=person_model, resource=person_list)
        )
        qs = QueryStringManager(
            {}, person_schema, allow_disable_pagination=True, max_page_size=100
        )
        count, collection = dl.get_collection(qs, {})

    assert isinstance(collection, list)
    assert count >= 1


def test_get_collection_with_sa_select_ignores_as_query_true(
    db, person_model, person_list, person_schema, person, app
):
    """sa.Select cannot be handed back as a lazy query object, so as_query=True
    must be ignored and a fully-executed list must always be returned."""
    app.config["PAGE_SIZE"] = 20
    with app.app_context():
        dl = SelectQueryDataLayer(
            dict(session=db.session, model=person_model, resource=person_list)
        )
        qs = QueryStringManager(
            {}, person_schema, allow_disable_pagination=True, max_page_size=100
        )
        count, collection = dl.get_collection(qs, {}, as_query=True)

    assert isinstance(collection, list)
    assert not isinstance(collection, sqlalchemy.Select)


# ---------------------------------------------------------------------------
# get_collection with orm.Query honours as_query=True (returns query, not list)
# ---------------------------------------------------------------------------


def test_get_collection_with_orm_query_as_query_true_returns_query_object(
    db, person_model, person_list, person_schema, person, app
):
    """When query() returns an orm.Query and as_query=True, get_collection must
    return the query object itself — not a materialised list.  This is the lazy
    path gated by _is_select(); if it regresses, callers that depend on deferred
    execution would silently get a list instead."""
    app.config["PAGE_SIZE"] = 20
    with app.app_context():
        dl = SqlalchemyDataLayer(
            dict(session=db.session, model=person_model, resource=person_list)
        )
        qs = QueryStringManager(
            {}, person_schema, allow_disable_pagination=True, max_page_size=100
        )
        count, collection = dl.get_collection(qs, {}, as_query=True)

    assert not isinstance(collection, list)
    assert _is_select(collection) is False  # it's an orm.Query


# ---------------------------------------------------------------------------
# filter_query with sa.Select actually narrows results
# ---------------------------------------------------------------------------


def test_filter_query_with_sa_select_filters_results(
    db, person_model, person_list, person, person_2
):
    """filter_query() calls .filter() on sa.Select (SA 2.x alias for .where()).
    Verify the filter actually narrows results — not just that it returns without error."""
    dl = SqlalchemyDataLayer(
        dict(session=db.session, model=person_model, resource=person_list)
    )
    query = sqlalchemy.select(person_model)
    filter_info = [{"name": "name", "op": "eq", "val": person.name}]

    filtered = dl.filter_query(query, filter_info, person_model)

    assert isinstance(filtered, sqlalchemy.Select)
    results = list(db.session.scalars(filtered))
    assert all(p.name == person.name for p in results)
    # person_2 has a different name, so must be absent
    assert not any(p.person_id == person_2.person_id for p in results)


# ---------------------------------------------------------------------------
# sort_query with sa.Select produces ordered results
# ---------------------------------------------------------------------------


def test_sort_query_with_sa_select_orders_results(
    db, person_model, person_list, person, person_2
):
    """sort_query() calls .outerjoin() and .order_by() on sa.Select.
    Verify the resulting query is still a Select and that results are ordered."""
    dl = SqlalchemyDataLayer(
        dict(session=db.session, model=person_model, resource=person_list)
    )
    query = sqlalchemy.select(person_model)
    sort_info = [{"field": "name", "order": "asc"}]

    sorted_q = dl.sort_query(query, sort_info)

    assert isinstance(sorted_q, sqlalchemy.Select)
    results = list(db.session.scalars(sorted_q))
    names = [p.name for p in results]
    assert names == sorted(names)
