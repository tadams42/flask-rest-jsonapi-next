"""
semi-transaprent, drop-in and optional support for rapidjson

clients of this module can use it like this:

    from json_utilities import json, JSONEncoder

and it will ensure that `rapidjson` is used if installed
"""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

_HAS_ARROW = False
try:
    from arrow import Arrow

    _HAS_ARROW = True
except ImportError:
    pass

_HAS_RAPIDJSON = False
try:
    import rapidjson as json

    _HAS_RAPIDJSON = True
except ImportError:
    import json


if _HAS_RAPIDJSON:

    class JSONEncoder:
        def __init__(self, *args, **kwargs):
            rjkwargs = dict(
                skip_invalid_keys=kwargs.get("skipkeys", False),
                ensure_ascii=kwargs.get("ensure_ascii", True),
                write_mode=json.WM_COMPACT,
                indent=kwargs.get("indent", None),
                sort_keys=kwargs.get("sort_keys", False),
                number_mode=json.NM_DECIMAL,
                datetime_mode=json.DM_ISO8601,
                uuid_mode=json.UM_CANONICAL,
                # bytes_mode=None,
                # iterable_mode=IM_ANY_ITERABLE,
                # mapping_mode=MM_ANY_MAPPING,
            )
            encoder = json.Encoder(**rjkwargs)
            self.encode = encoder.__call__

else:

    class JSONEncoder(json.JSONEncoder):
        _DATES_TIMES = (
            date,
            datetime,
        )
        if _HAS_ARROW:
            _DATES_TIMES = (
                date,
                datetime,
                Arrow,
            )

        def default(self, obj):
            if isinstance(obj, self._DATES_TIMES):
                return obj.isoformat()
            elif isinstance(obj, UUID):
                return str(obj)
            elif isinstance(obj, Decimal):
                return str(obj)
            return json.JSONEncoder.default(self, obj)
