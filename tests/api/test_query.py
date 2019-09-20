import datetime
import pytest

from .. import EventMongoQuery


def test_event_query_can_init_with_empty_options():
    query = EventMongoQuery()
    assert not query.options


def test_event_query_can_init_with_valid_options():
    date = datetime.datetime.utcnow()
    query = EventMongoQuery(offset=30, clients=[1, 2], start_date=date)
    test_dict = {
        "offset": 30,
        "clients": [1, 2],
        "start_date": date,
    }
    assert query.options == test_dict


def test_event_query_raises_with_invalid_options():
    with pytest.raises(AttributeError):
        EventMongoQuery(foo="bar")


def test_event_query_can_get_value():
    query = EventMongoQuery(group_by=["client"], clients=[1, 2], offset=50)
    assert query.get_value("clients") == [1, 2]
    assert query.get_value("limit") == 5
    assert query.get_value("offset") == 50
    assert query.get_value("group_by") == ["client"]
    assert not query.get_value("order_by")


def test_event_query_can_get_start_date():
    date = datetime.datetime.utcnow()
    query = EventMongoQuery(start_date=date)
    assert query.get_start_date() == date
    query = EventMongoQuery()
    assert not query.get_start_date()


def test_event_query_can_get_end_date():
    date = datetime.datetime.utcnow()
    query = EventMongoQuery(end_date=date)
    assert query.get_end_date() == date
    query = EventMongoQuery()
    assert not query.get_end_date()


def test_event_query_can_collect_name_and_values():
    query = EventMongoQuery(clients=[1, 2], client_groups=[3, 4])
    test_dict = {"client": [1, 2], "client_group": [3, 4]}
    assert query.collect_name_and_values() == test_dict


def test_event_query_can_get_timestamp_dict_with_start_and_end_dates():
    start_date = datetime.datetime.utcnow().replace(hour=1)
    end_date = datetime.datetime.utcnow().replace(hour=10)
    query = EventMongoQuery(start_date=start_date, end_date=end_date)
    test_dict = {
        "timestamp": {
            "$gte": start_date,
            "$lte": end_date,
        }
    }
    assert query.get_timestamp_dict() == test_dict


def test_event_query_can_get_timestamp_dict_with_start_date():
    start_date = datetime.datetime.utcnow().replace(hour=1)
    query = EventMongoQuery(start_date=start_date)
    test_dict = {"timestamp": {"$gte": start_date}}
    assert query.get_timestamp_dict() == test_dict


def test_event_query_can_get_timestamp_dict_with_end_date():
    end_date = datetime.datetime.utcnow().replace(hour=10)
    query = EventMongoQuery(end_date=end_date)
    test_dict = {"timestamp": {"$lte": end_date}}
    assert query.get_timestamp_dict() == test_dict


def test_event_query_can_get_timestamp_dict_with_no_date():
    query = EventMongoQuery()
    assert not query.get_timestamp_dict()


def test_event_query_can_get_match_query_dict_with_date():
    end_date = datetime.datetime.utcnow().replace(hour=10)
    query = EventMongoQuery(clients=[1, 2], end_date=end_date)
    test_dict = {
        "$match":
            {
                "timestamp": {"$lte": end_date},
                "client": {"$in": [1, 2]}
            }
    }
    assert query.get_match_query_dict() == test_dict


def test_event_query_can_get_match_query_dict_without_date():
    query = EventMongoQuery(clients=[1, 2])
    test_dict = {
        "$match":
            {
                "client": {"$in": [1, 2]}
            }
    }
    assert query.get_match_query_dict() == test_dict


def test_event_query_can_get_match_query_dict_with_date_and_valid():
    end_date = datetime.datetime.utcnow().replace(hour=10)
    query = EventMongoQuery(clients=[1, 2], valid=True, end_date=end_date)
    test_dict = {
        "$match":
            {
                "timestamp": {"$lte": end_date},
                "client": {"$in": [1, 2]},
                "valid": {"$eq": True},
            }
    }
    assert query.get_match_query_dict() == test_dict


def test_event_query_can_build_pipeline():
    start_date = datetime.datetime.utcnow().replace(hour=1)
    end_date = datetime.datetime.utcnow().replace(hour=10)
    query = EventMongoQuery(
        clients=[1, 2],
        valid=True,
        group_by=["client"],
        order_by=["client"],
        start_date=start_date,
        end_date=end_date,
    )
    pipeline = query.build_pipeline()
    test_pipeline = [
        {'$match': {
            'client': {'$in': [1, 2]},
            'valid': {'$eq': True},
            'timestamp': {
                '$gte': start_date,
                '$lte': end_date,
            }
        }},
        {'$sort': {'_id': 1, 'client': 1}},
        {'$group': {
            '_id': {'client': '$client'},
           'mean': {'$avg': '$value'},
           'sum': {'$sum': '$value'},
           'count': {'$sum': 1}}},
        {'$skip': 0},
        {'$limit': 5},
    ]

    assert pipeline == test_pipeline
