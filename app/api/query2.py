import pymongo

from .utils import TimeRangeNameEnum
from ..settings import (DEFAULT_PAGE_LIMIT,
                        MONGO_CLIENT,
                        MONGO_DB_NAME,
                        MONGO_COLLECTION_NAME)

# TODO: Move to settings
collection = MONGO_CLIENT[MONGO_DB_NAME][MONGO_COLLECTION_NAME]

FILTERS = ["offset", "limit", "group_by", "order_by"]

ARRAYS = ["client", "client_group", "device_type", "category"]
EQUALS = ["valid"]
DIMENSIONS = ARRAYS + EQUALS + ["date"]

MONGO_NAMES = {
    "clients": "client",
    "client_groups": "client_group",
    "device_types": "device_type",
    "categories": "category",
    "valid": "valid",
    "date": "timestamp",
}

MONGO_MATCH_NAMES = MONGO_NAMES.copy()
MONGO_MATCH_NAMES.pop("date")

DEFAULTS = {
    "offset": 0,
    "limit": DEFAULT_PAGE_LIMIT,
    "group_by": ["client", "client_group", "device_type", "category", "valid",
                 "timestamp"]
}


def get_value_or_default(options, key, default=None):
    return options.get(key, DEFAULTS.get(key, default))


def get_sort_query(options):
    values = set(get_value_or_default(options, "order_by", []))
    descendings = set(filter(lambda x: x.startswith('-'), values))
    sort_dict = {}

    def add_values(values, sign):
        sort_dict.update({value.lstrip('-'): sign for value in values})

    add_values(descendings, pymongo.DESCENDING)
    add_values((values - descendings), pymongo.ASCENDING)
    return sort_dict


def replace_object(values, obj, replace="timestamp"):
    if obj in values:
        values.remove("date")
        values.append(replace)


def get_group_ids(options):
    values = get_value_or_default(options, "group_by", DIMENSIONS)
    replace_object(values, "date")
    return {name: f"${name}" for name in values}


def get_timestamp_query(options):
    timestamp = {}

    def add_date(name, operator):
        date = get_value_or_default(options, name)
        if date:
            timestamp[operator] = date

    add_date("start_date", "$gte")
    add_date("end_date", "$lte")
    return timestamp


def get_match_query(options):
    match_query = {}
    for name in MONGO_MATCH_NAMES:
        value = get_value_or_default(options, name)
        if value:
            field_name = MONGO_NAMES[name]
            operator = "$in" if field_name in ARRAYS else "$eq"
            match_query[field_name] = {operator: value}

    if "start_date" in options or "end_date" in options:
        match_query["timestamp"] = get_timestamp_query(options)

    return match_query


def build_pipeline(**kwargs):
    options = kwargs.copy()
    sort_query = {'_id': 1}
    sort_query.update(get_sort_query(options))
    pipeline = [
        {'$match': get_match_query(options)},
        {'$sort': sort_query},
        {'$group': {
            '_id': get_group_ids(options),
            'mean': {'$avg': '$value'},
            'sum': {'$sum': '$value'},
            'count': {'$sum': 1}}},
        {'$skip': get_value_or_default(options, "offset")},
        {'$limit': get_value_or_default(options, "limit")},
    ]
    return pipeline


def verify_options(options):
    if options:
        all_names = FILTERS + list(MONGO_NAMES) + TimeRangeNameEnum.values()
        extra = set(options) - set(all_names)
        if extra:
            raise AttributeError(f"Invalid Extra Parameter(s): {extra}")
    return True


def run_event_query(**kwargs):
    options = kwargs.copy()
    verify_options(options)
    query = collection.aggregate(
        build_pipeline(**options)
    )

    pagination = {
        "offset": get_value_or_default(options, "offset"),
        "page_size": get_value_or_default(options, "limit"),
        "total_count": collection.count_documents({}),
    }

    # TODO: Maybe this should be lazy. Assuming pagination is low
    return list(query), pagination
