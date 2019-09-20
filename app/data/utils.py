#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Generate random data for the test.

    python generate-data.py [DAYS] [EVENTS_PER_DAY]

    Copyright: Stylight

"""

import datetime as _dt
import math as _math
import random as _random
import uuid as _uuid

random = _random.SystemRandom()

DEVICES = ['desktop'] * 3 + ['mobile'] * 4 + ['tablet'] * 2 + [None]
CATEGORIES = [random.randint(100, 1000) for _ in range(32)] + [None]
CLIENTS = [random.randint(100, 1000) for _ in range(128)]
CLIENT_GROUPS = {}

for cl in CLIENTS:
    CLIENT_GROUPS[cl] = random.randint(10, 20)

TODAY = _dt.datetime.combine(_dt.date.today(), _dt.time(0, 0, 0))


def _random_ts(start, end, count):
    return [random.random() * (end - start) + start for _ in range(count)]


def _generate_event(ts):
    client = random.choice(CLIENTS)
    return {
        'id': str(_uuid.uuid4()),
        'device_type': random.choice(DEVICES),
        'category': random.choice(CATEGORIES),
        'client': client,
        'client_group': CLIENT_GROUPS[client],
        'timestamp': ts,
        'valid': random.choice([True] * 8 + [False] * 2),
        'value': float("%.2f" % (random.random() * 100)),
    }


def get_events(days, events_per_day):
    for d in range(-days, 0):
        start = TODAY + _dt.timedelta(days=d)
        end = TODAY + _dt.timedelta(days=(d + 1))
        count = _math.ceil(random.randrange(8, 13) / 10 * events_per_day)
        for ts in sorted(_random_ts(start, end, count)):
            yield _generate_event(ts)
