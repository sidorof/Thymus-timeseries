"""
This module implements a class derived from dicts for working with timeseries.

"""

from copy import deepcopy
import json

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

    Usage:
        tssdict = TssDict(values=None)

    values can be a dict, list, using the key from each timeseries as the
    dict key.


    """

    timeseries_class = Timeseries

    def __init__(self, values=None, split=None):
        dict.__init__(self)  # only did this to satisfy pylint

        if isinstance(values, dict):
            for key, values in values.items():
                self[key] = values
        elif isinstance(values, list):
            for i, ts_tmp in enumerate(values):
                ts_tmp = values[i]
                self[ts_tmp.key] = ts_tmp
        else:
            # nothing to do.
            pass

        if split:
            if isinstance(split, Timeseries):
                for key, values in self.split_timeseries(split):
                    self[key] = values

    @staticmethod
    def split_timeseries(ts):
        """
        Splits up a timeseries so that each column is a separate timeseries
        within a tssdict.

        The only caveat is that there must be a column in ts.columns for each
        column in the timeseries. Since that is discretionary, it must be
        checked.
        """
        error = "The number of column names must match tseries.shape[1]."
        if ts.columns is None:
            raise ValueError(error)
        if len(ts.columns) != ts.tseries.shape[1]:
            raise ValueError(error)

        tmp_list = []
        for col in range(len(ts.columns)):
            tmp_ts = Timeseries()
            tmp_ts.dseries = ts.dseries
            tmp_ts.tseries = ts.tseries[:, col]
            tmp_ts.columns = [ts.columns[col]]

            tmp_list.append((ts.columns[col], tmp_ts))

        return tmp_list

    def min_date(self):
        """
        Returns the earliest date as a tuple(datetime, key in the group).
        """
        min_date = None
        min_key = None

        for key, values in self.items():
            if isinstance(values, Timeseries):
                date = values.start_date("datetime")
                if min_date is not None:
                    if date < min_date:
                        min_date = date
                        min_key = key
                else:
                    min_date = date
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
                date = values.end_date("datetime")
                if max_date is not None:
                    date = date
                    if date > max_date:
                        max_date = date
                        max_key = key
                else:
                    max_date = date
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

        for key, ts in self.items():
            if isinstance(ts, Timeseries):
                if ts.tseries is not None:
                    length = ts.tseries.shape[0]
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
        min_length = None
        min_key = None

        for key, ts in self.items():
            if isinstance(ts, Timeseries):
                if ts.tseries is None:
                    return None

                length = ts.tseries.shape[0]
                if min_length is None:
                    min_length = length
                else:
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

            if isinstance(tmp, Timeseries):
                try:
                    all_values.append(tmp.tseries[tmp.row_no(date)])
                except ValueError:
                    if notify:
                        raise ValueError(
                            "ts %s does not have a value on %s" % (key, date)
                        )
                    else:
                        all_values.append(None)

            else:
                raise ValueError("Unsupported values in dict")

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
            """This function combines an item with an existing timeseries."""
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
                        pad=pad,
                    )

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

    def to_dict(self, dt_fmt="str", data_list=True):
        """
        This function outputs the entirety of the object as a dict with
        the timeseries components as a dict as well.

        This enables building JSON formatted files from objects that include
        TssDict objects.

        Usage:
            self.to_dict(dt_fmt='str', data_list=True)
        """
        outdict = {}

        for key, ts in self.items():
            outdict[key] = ts.to_dict(dt_fmt=dt_fmt, data_list=data_list)

        return outdict

    def from_dict(self, tssdict):
        """
        This function loads from a dict.

        The format of the dict of timeseries is assumed to use the form from
        Timeseries.to_dict(dt_fmt='str')
        """
        self.clear()

        for key, value in tssdict.items():
            self[key] = self.timeseries_class().from_dict(value)

        return self

    def to_json(self, indent=2, dt_fmt="str", data_list=True):
        """
        This function returns the timeseries dict in JSON format.

        Usage:
            self.to_json(indent=2, dt_fmt='str', data_list=True)

        indent: indenting in the JSON output
        dt_fmt: formatting of the dates. Look at help for
                    Timeseries.to_dict
        data_list: Whether data uses a dict for dates as keys or
                   simply a list.
                   Default is for a list. Otherwise, sorting the
                   timeseries in the list would be required.

        """
        return json.dumps(
            self.to_dict(dt_fmt=dt_fmt, data_list=data_list), indent=indent
        )

    def from_json(self, json_str):
        """
        This function loads a JSON string and applies it to the object.
        """
        self.clear()

        tss_tmp = json.loads(json_str)

        if isinstance(tss_tmp, dict):
            for key, value in tss_tmp.items():
                self[key] = self.timeseries_class().from_dict(value)

        else:
            raise ValueError(
                "Incoming JSON string does not start with a dict."
            )

        return self
