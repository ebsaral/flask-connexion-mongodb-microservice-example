import datetime

from .. import build_pipeline


def test_build_pipeline():
    start_date = datetime.datetime.utcnow().replace(hour=1)
    end_date = datetime.datetime.utcnow().replace(hour=10)
    pipeline = build_pipeline(
        clients=[1, 2],
        valid=True,
        group_by=["client"],
        order_by=["client"],
        start_date=start_date,
        end_date=end_date,
    )
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
