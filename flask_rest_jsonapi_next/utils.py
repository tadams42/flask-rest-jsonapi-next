# -*- coding: utf-8 -*-
# isort: skip_file
# fmt: off

from flask import current_app

from .json_utilities import json, JSONEncoder, _HAS_RAPIDJSON

def json_dumps(obj):
    sort_keys = current_app.config.get("JSON_SORT_KEYS", False)

    if _HAS_RAPIDJSON:
        return json.dumps(
            obj,
            sort_keys=sort_keys,
            number_mode=json.NM_DECIMAL,
            datetime_mode=json.DM_ISO8601,
            uuid_mode=json.UM_CANONICAL
        )

    else:
        return json.dumps(obj, sort_keys=sort_keys, cls=JSONEncoder)

# fmt: on
