"""
This module implements a class derived from lists for working with timeseries.

"""

from copy import deepcopy
import json

from .timeseries import Timeseries


class TssList(list):
    """
    This class is a way of handling some the routine tasks for groups
    of timeseries.

    Assumption:
        This is a list of timeseries of common interest

    Usage:
        tss = TssList(tss=None)  # where tss is a list of timeseries


    """

    timeseries_class = Timeseries

    def __init__(self, tss=None):
        list.__init__(self)  # only did this to satisfy pylint
        if tss is None:
            pass
        elif isinstance(tss, list):
            self.extend(tss)
        elif isinstance(tss, tuple):
            self.extend(tss)
        else:
            raise ValueError("Initialization requires either a list or None")

    def min_date(self):
        """
        Returns the earliest date as a datetime.

        By using a datetime, there is no need to distinguish whether time
        series are ordinal or timestamp or mixed.

        """

        dates = [
            ts.start_date("datetime") for ts in self if ts.dseries is not None
        ]

        if dates:
            return min(dates)
        else:
            return None

    def max_date(self):
        """
        Returns the latest date

        """

        dates = [
            ts.end_date("datetime") for ts in self if ts.dseries is not None
        ]

        if dates:
            return max(dates)
        else:
            return None

    def get_values(self, date, notify=False):
        """
        This function finds the values current to the date for the tickers.

        The point of notify is not fail gracefully if necessary.
        """

        values = []
        for idx, ts_tmp in enumerate(self):
            try:
                values.append(ts_tmp.tseries[ts_tmp.row_no(rowdate=date)])
            except ValueError:
                if notify:
                    raise ValueError(
                        "ts %s does not have a value on %s" % (idx, date)
                    )
                else:
                    values.append(None)

        return tuple(values)

    def combine(self, discard=True, pad=None):
        """
        This function combines all timeseries into one by applying the combine
        function to each timeseries.

        Usage:
            combine(self, discard=True, pad=None)

        returns ts

        """

        if len(self) > 1:
            return self[0].combine(self[1:], discard=discard, pad=pad)
        else:
            return self[0].clone()

    def clone(self):
        """
        Returns a new copy of the object.
        """

        return deepcopy(self)

    def as_dict(self):
        """
        This function returns a dict with keys being the timeseries key.

        If keys are missing, an error is raised.
        """

        for ts_tmp in self:
            if ts_tmp.key == "" or ts_tmp.key is None:
                raise ValueError("There must be a key for each timeseries.")

        return dict([(ts_tmp.key, ts_tmp) for ts_tmp in self])

    def to_list(self, dt_fmt="str", data_list=True):
        """
        This function builds a list of timeseries that are in the form of
        dict objects for use when build JSON formatted file.
        """

        outlist = []

        for ts in self:
            outlist.append(ts.to_dict(dt_fmt=dt_fmt, data_list=data_list))

        return outlist

    def to_json(self, indent=2, dt_fmt="str", data_list=True):
        """
        This function returns the timeseries list in JSON format.

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
            self.to_list(dt_fmt=dt_fmt, data_list=data_list), indent=indent
        )

    def from_dict(self, tsslist):
        """
        This function loads a list of dicts that will be converted to
        time series objects.
        """
        self.clear()

        for item in tsslist:
            self.append(self.timeseries_class().from_dict(item))

        return self

    def from_json(self, json_str):
        """
        This function loads a JSON string and applies it to the object.
        """
        self.clear()

        tss_tmp = json.loads(json_str)

        for item in tss_tmp:
            self.append(self.timeseries_class().from_dict(item))

        return self
