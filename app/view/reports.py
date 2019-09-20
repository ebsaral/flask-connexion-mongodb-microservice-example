from benedict import benedict

from ..api.query2 import run_event_query


def get_value_or_default(dictionary, path, default=None):
    ben_dict = benedict(dictionary)
    if path not in ben_dict:
        return default
    else:
        return ben_dict[path] or default

def normalize_report_query(results):
    data = []

    for result in results:
        data.append(
            {
                "category": get_value_or_default(result, "_id.category", 0),
                "client": get_value_or_default(result, "_id.client", 0),
                "client_group": get_value_or_default(
                    result, "_id.client_group", 0),
                "valid": get_value_or_default(result, "_id.valid", None),
                "device_type": get_value_or_default(result, "_id.device_type"),
                "day": "2019-01-01", # TODO: Filter out on MongoDB
                "mean": get_value_or_default(result, "mean", 0.0),
                "sum": get_value_or_default(result, "sum", 0.0),
            }
        )
    return data


def get(**kwargs):
    result, pagination = run_event_query(**kwargs)
    normalized_result = normalize_report_query(result)

    response = {
        "rows": normalized_result,
        "pagination": pagination,
    }

    return response, 200
