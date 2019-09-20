import pymongo

from ..settings import (DEFAULT_PAGE_LIMIT,
                        MONGO_CLIENT,
                        MONGO_DB_NAME,
                        MONGO_COLLECTION_NAME)
from .utils import TimeRangeNameEnum


class EventMongoQuery: # TODO: Deprecate this class
    """
    This is a class based implementation of query manipulation
    """
    collection = MONGO_CLIENT[MONGO_DB_NAME][MONGO_COLLECTION_NAME]

    SUPPORTED_FILTERS = [
        "offset", "limit", "group_by", "order_by"
    ]

    SUPPORTED_ARRAYS = [
        "client",
        "client_group",
        "device_type",
        "category",
    ]

    NAMES_TO_REPLACE = {
        "date": "timestamp",
    }

    MONGO_NAMES = {
        "clients": "client",
        "client_groups": "client_group",
        "device_types": "device_type",
        "categories": "category",
        "valid": "valid",
        "date": "timestamp",
    }

    EXCLUDE_FROM_MATCH_QUERY = ["date"]

    DEFAULTS = {
        "offset": 0,
        "limit": DEFAULT_PAGE_LIMIT,
        "group_by": [
            "client",
            "client_group",
            "device_type",
            "category",
            "valid",
            "date",
        ]
    }

    def __init__(self, **options):
        self.options = options.copy()
        self._verify_options()

    def _verify_options(self):
        if self.options:
            ts = TimeRangeNameEnum.values()
            all_names = self.SUPPORTED_FILTERS + list(self.MONGO_NAMES) + ts
            extra = set(self.options) - set(all_names)
            if extra:
                raise AttributeError(f"Invalid Extra Parameter(s): {extra}")
        return True

    def get_value(self, key):
        value = self.options.get(key)
        if value is None:
            value = self.DEFAULTS.get(key, None)
        return value

    def get_start_date(self):
        return self.get_value(TimeRangeNameEnum.START_DATE.value)

    def get_end_date(self):
        return self.get_value(TimeRangeNameEnum.END_DATE.value)

    def collect_name_and_values(self):
        name_value_dict = {}
        for api_key in self.MONGO_NAMES:
            if api_key in self.EXCLUDE_FROM_MATCH_QUERY:
                continue
            value = self.get_value(api_key)
            if value:
                name_value_dict[self.MONGO_NAMES[api_key]] = value
        return name_value_dict

    def get_timestamp_dict(self):
        timestamp_dict = {}
        start_date = self.get_start_date()
        end_date = self.get_end_date()
        if start_date:
            timestamp_dict["$gte"] = start_date
        if end_date:
            timestamp_dict["$lte"] = end_date
        return timestamp_dict and {self.MONGO_NAMES["date"]: timestamp_dict}

    def get_match_query_dict(self):
        name_value_pairs = self.collect_name_and_values()
        in_dict = {}
        for name, value in name_value_pairs.items():
            operator = "$in" if name in self.SUPPORTED_ARRAYS else "$eq"
            in_dict[name] = {operator: value}
        in_dict.update(self.get_timestamp_dict())
        return in_dict and {"$match": in_dict}

    def get_skip_dict(self):
        return {"$skip": self.get_value("offset")}

    def get_limit_dict(self):
        return {"$limit": self.get_value("limit")}

    def get_group_by_dict(self):
        values = self.get_value("group_by")
        values = list(
            map(
                lambda x: self.NAMES_TO_REPLACE[x]
                if x in self.NAMES_TO_REPLACE else x,
                values
            )
        )

        group_by_dict = {}
        for value in values:
            group_by_dict[value] = f"${value}"

        group_inner_dict = {
            "_id": group_by_dict,
            "mean": {"$avg": "$value"},
            "sum": {"$sum": "$value"},
            "count": {"$sum": 1},
        }

        group_dict = {
            "$group": group_inner_dict
        }
        return group_by_dict and group_dict

    def get_order_by_dict(self):
        values = self.get_value("order_by")
        if not values:
            return None

        order_by_dict = {"_id": 1}
        for value in values:
            if value.startswith('-'):
                value = value[1]
                order = pymongo.DESCENDING
            else:
                order = pymongo.ASCENDING
            order_by_dict[value] = order
        return order_by_dict and {"$sort": order_by_dict}

    def build_pipeline(self):
        pipeline = []
        match_dict = self.get_match_query_dict()
        match_dict and pipeline.append(match_dict)
        pipeline.append(self.get_order_by_dict())
        group_dict = self.get_group_by_dict()
        group_dict and pipeline.append(group_dict)
        pipeline.append(self.get_skip_dict())
        pipeline.append(self.get_limit_dict())
        return pipeline

    def query(self):
        aggregate_pipeline = self.build_pipeline()
        print(aggregate_pipeline)
        query = self.collection.aggregate(
            aggregate_pipeline
        )
        return list(query)
