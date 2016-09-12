"""
This module implements a class derived from dicts for working with timeseries.

"""

from copy import deepcopy

from .tsslist import TssList
from .timeseries import Timeseries


class TssDict(dict):
    """
    This class is a way of handling some of the routine tasks for groups
    of timeseries.

    Assumption:
        This is a dict of timeseries that are keyed by tickers, etc. Or, it
        could be a dict of keys that hold lists of timeseries with some
        commonality.

    Useage:
        tssdict = TssDict(values=None)

    values can be a dict, list, using the key from each timeseries as the
    dict key.


    """
    def __init__(self, values=None):

        dict.__init__(self)   # only did this to satisfy pylint

        if isinstance(values, dict):
            for key, values in values.items():
                self[key] = values
        elif isinstance(values, list):
            for i in range(len(values)):
                ts_tmp = values[i]
                self[ts_tmp.key] = ts_tmp
        else:
            # nothing to do.
            pass

    def min_date(self):
        """
        Returns the earliest date as a tuple(datetime, key in the group).
        """
        min_date = None
        min_key = None

        for key, values in self.items():

            if isinstance(values, Timeseries):
                date = values.start_date('datetime')
                if min_date is not None:
                    if date < min_date:
                        min_date = date
                        min_key = key
                else:
                    min_date = date
                    min_key = key

            elif isinstance(values, list):
                if min_date is not None:
                    date = values.min_date()
                    if date < min_date:
                        min_date = date
                        min_key = key
                else:
                    min_date = TssList(values).min_date()
                    min_key = key

            elif isinstance(values, TssDict):
                if min_date is not None:
                    date = values.min_date()
                    if date < min_date:
                        min_date = date
                        min_key = key
                else:
                    min_date, _ = values.min_date()
                    min_key = key

            else:
                # what is it?
                raise ValueError("Unsupported values in dict")

        return (min_date, min_key)

    def max_date(self):
        """
        Returns the latest date, key in the group

        If more than one has the same max date, simply one of them is
        returned.
        """
        max_date = None
        max_key = None

        for key, values in self.items():

            if isinstance(values, Timeseries):
                date = values.end_date('datetime')
                if max_date is not None:
                    date = date
                    if date > max_date:
                        max_date = date
                        max_key = key
                else:
                    max_date = date
                    max_key = key

            elif isinstance(values, list):
                if max_date is not None:
                    date = values.max_date()
                    if date > max_date:
                        max_date = date
                        max_key = key
                else:
                    max_date = TssList(values).max_date()
                    max_key = key

            elif isinstance(values, TssDict):
                if max_date is not None:
                    date = values.max_date()
                    if date > max_date:
                        max_date = date
                        max_key = key
                else:
                    max_date, _ = values.max_date()
                    max_key = key

            else:
                # what is it?
                raise ValueError("Unsupported values in dict")

        return (max_date, max_key)

    def longest_ts(self):
        """
        This function returns item with the longest timeseries.

        """
        max_length = 0
        max_key = None

        for key, values in self.items():

            if isinstance(values, Timeseries):
                length = values.tseries.shape[0]
                if length > max_length:
                    max_length = length
                    max_key = key

            elif isinstance(values, list):
                length = max([ts.tseries.shape[0] for ts in values])
                if length > max_length:
                    max_length = length
                    max_key = key

            elif isinstance(values, TssDict):
                length, _ = values.longest_ts()
                if length > max_length:
                    max_length = length
                    max_key = key

            else:
                # what is it?
                raise ValueError("Unsupported values in dict")

        return (max_length, max_key)

    def shortest_ts(self):
        """
        This function returns item with the shortest timeseries.

        """
        min_length = 0
        min_key = None

        for key, values in self.items():

            if isinstance(values, Timeseries):
                length = values.tseries.shape[0]
                if length < min_length:
                    min_length = length
                    min_key = key

            elif isinstance(values, list):
                length = min([ts.tseries.shape[0] for ts in values])
                if length < min_length:
                    min_length = length
                    min_key = key

            elif isinstance(values, TssDict):
                length, _ = values.longest_ts()
                if length < min_length:
                    min_length = length
                    min_key = key

            else:
                # what is it?
                raise ValueError("Unsupported values in dict")

        return (min_length, min_key)

    def get_values(self, date, keys=None, notify=False):
        """
        This function finds the values as the date. If keys come in as a list
        the order of the values can be controlled or to limit the timeseries
        selected.

        The point of notify is to not fail gracefully if necessary.
        """

        if keys is None:
            keys = self.keys()

        all_values = []

        for key in keys:

            tmp = self[key]

            if isinstance(tmp, TssList):
                all_values.append(tmp.get_values(date, notify=notify))

            elif isinstance(tmp, list):

                all_values.append(TssList(tmp).get_values(date, notify=notify))

            elif isinstance(tmp, Timeseries):

                try:
                    all_values.append(tmp.tseries[tmp.row_no(date)])
                except ValueError:
                    if notify:
                        raise ValueError(
                            "ts %s does not have a value on %s" % (key, date))
                    else:
                        all_values.append(None)

            else:

                # thinking about doing TssDict but not sure about passing up
                # the values and keys back up.
                pass

        return (tuple(all_values), tuple(keys))

    def combine(self, keys=None, discard=True, pad=None):
        """
        This function combines all timeseries into one. The point of keys is
        that you have the ability to control the order of the columns.

        Usage:
            combine(self, keys=None, pad=None)

        returns ts, keys

        """

        def iter_combine(ts1, item, discard=discard, pad=pad):
            """This function combines an item with an existing timeseries. """
            if isinstance(item, TssList):

                if ts1 is None:
                    ts1 = item.combine(discard=discard, pad=pad)
                else:
                    ts1.combine(item, discard=discard, pad=pad)

            elif isinstance(item, list):

                if ts1 is None:
                    ts1 = TssList(item).combine(discard=discard, pad=pad)
                else:
                    ts1.combine(item, discard=discard, pad=pad)

            elif isinstance(item, Timeseries):

                if ts1 is None:
                    ts1 = item.clone()
                else:
                    ts1 = ts1.combine(item, discard=discard, pad=pad)

            elif isinstance(item, TssDict):

                if ts1 is None:
                    ts1, _ = item.combine(discard=discard, pad=pad)
                else:
                    ts1.combine(
                        item.combine(discard=discard, pad=pad),
                        discard=discard,
                        pad=pad)

            else:
                raise ValueError("Unsupported type in for \n%s" % (item))

            return ts1

        if keys is None:
            keys = self.keys()

        if len(keys) == 0:
            return None

        ts1 = None
        for key in keys:
            ts1 = iter_combine(ts1, self[key], discard=discard, pad=pad)

        return ts1, tuple(keys)

    def clone(self):
        """
        Returns a new copy of the object.
        """

        return deepcopy(self)
