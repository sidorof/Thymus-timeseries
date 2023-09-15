# freq_conversions.py
"""
This module converts timeseries from one type to another.

"""

import numpy as np

from .constants import FREQ_D, FREQ_M, FREQ_Q, FREQ_Y
from .constants import FREQ_H, FREQ_MIN, FREQ_SEC
from .constants import TS_ORDINAL, TS_TIMESTAMP

HIERARCHY = (FREQ_SEC, FREQ_MIN, FREQ_H, FREQ_D, FREQ_M, FREQ_Q, FREQ_Y)


def _q_test(date, kwargs):
    """
    Computes quarterly indicators.

    No expectation of using kwargs in this. It is for consistency.
    """

    return date.month % 3 == 0


def _weekday_test(date, kwargs):
    """
    Computes weekly indicators.
    """

    if "weekday" in kwargs:
        weekday = kwargs["weekday"]

        if date.weekday() == weekday:
            return 1
        else:
            return 0
    else:
        return date.weekday()


def _filter_dates(dates, freq, kwargs):
    """
    This function filters dates to indicate end of periods for ordinals.
    """

    indicator = DATETIME_DICT[freq]

    if isinstance(indicator, str):
        # no special behavior
        indicators = np.fromiter(
            [date.__getattribute__(indicator) for date in dates],
            dtype=np.int32,
        )

        return np.argwhere(indicators[1:] - indicators[:-1] > 0)

    else:
        # apply a function
        indicators = np.fromiter(
            [indicator(date, kwargs) for date in dates], dtype=np.int32
        )

        return np.argwhere(indicators[1:] - indicators[:-1] > 0)


def _filter_idates(dates, freq, end_of_period, **kwargs):
    """
    This function filters dates to indicate end of periods for timestamps.
    """

    indicator = DATETIME_DICT[freq]

    if isinstance(indicator, str):
        # no special behavior
        indicators = np.fromiter(
            [date.__getattribute__(indicator) for date in dates],
            dtype=np.int32,
        )

        selected = np.argwhere(indicators[1:] - indicators[:-1] > 0)

        # check special case of start date

        if end_of_period is False:
            if dates[-1].__getattribute__(indicator) == 0:
                selected = np.append(selected, len(dates) - 1)

        return selected

    else:
        # apply a function -- here for completeness at the moment
        # could apply to 5 minute data for example
        return np.fromiter(
            [indicator(date, kwargs) for date in dates], dtype=np.int32
        )


DATETIME_DICT = {
    # 'sec': 'second',
    "min": "second",
    "h": "minute",
    "d": "hour",
    "w": _weekday_test,
    "m": "day",
    "q": _q_test,
    "y": "month",
}


def convert(ts, new_freq, include_partial=True, **kwargs):
    """
    This function converts a timeseries to another frequency. Conversion only
    works from a higher frequency to a lower frequency, for example daily to
    monthly.

    NOTE: add a gatekeeper for invalid kwargs.
    """

    new_ts = ts.clone()
    series_dir = ts.series_direction()
    new_ts.sort_by_date(reverse=True)

    freq_idx = HIERARCHY.index(ts.frequency)
    new_idx = HIERARCHY.index(FREQ_Q)
    daily_idx = HIERARCHY.index(FREQ_D)

    if freq_idx > new_idx:
        raise ValueError(
            "Cannot convert from %s to %s." % (ts.frequency, new_freq)
        )

    dates = new_ts.datetime_series()

    date_series_type = ts.get_date_series_type()
    if date_series_type == TS_ORDINAL:
        selected = _filter_dates(dates, new_freq, kwargs)
    elif date_series_type == TS_TIMESTAMP:
        selected = _filter_idates(
            dates, new_freq, end_of_period=ts.end_of_period
        )
    else:
        raise ValueError("Invalid date series type: %s" % (date_series_type))

    if selected.shape[0] > 0:
        if new_ts.end_of_period:
            selected += 1  # shift to start of next period

        if include_partial or freq_idx > daily_idx:
            if selected[0] != 0:
                # insert most recent date
                # selected = np.insert(selected, 0, 0)
                # np.insert(arr, obj, values, axis=None)
                selected = np.insert(selected, 0, 0)

        if freq_idx > daily_idx:
            # already processed (probably)
            if selected[-1] != len(dates) - 1:
                selected = np.append(selected, len(dates) - 1)

    new_ts.tseries = new_ts.tseries[selected.flatten()]

    new_ts.frequency = new_freq

    if new_freq == FREQ_D:
        # convert dates from timestamp to ordinal
        new_ts.dseries = np.fromiter(
            [date.toordinal() for date in np.array(dates)[selected]],
            dtype=np.int32,
        )
    else:
        new_ts.dseries = new_ts.dseries[selected]

    new_ts.dseries = new_ts.dseries.flatten()

    if series_dir != new_ts.series_direction():
        new_ts.reverse()

    return new_ts
