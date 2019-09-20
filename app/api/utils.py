from enum import Enum


class TimeRangeNameEnum(Enum):
    START_DATE = "start_date"
    END_DATE = "end_date"

    @staticmethod
    def values():
        return list(map(lambda e: e.value, iter(TimeRangeNameEnum)))
