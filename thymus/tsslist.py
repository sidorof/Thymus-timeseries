"""
This module implements a class derived from lists for working with timeseries.

"""

from copy import deepcopy


class TssList(list):
    """
    This class is a way of handling some the routine tasks for groups
    of timeseries.

    Assumption:
        This is a list of timeseries of common interest

    Useage:
        tss = TssList(tss=None)  # where tss is a list of timeseries


    """
    def __init__(self, tss=None):

        list.__init__(self)   # only did this to satisfy pylint

        if isinstance(tss, list):

            self.extend(tss)

    def min_date(self):
        """
        Returns the earliest date as a datetime.

        By using a datetime, there is no need to distinguish whether time
        series are ordinal or timestamp or mixed.

        """

        dates = [
            ts.start_date('datetime') for ts in self
            if ts.dseries is not None]

        if dates:
            return min(dates)
        else:
            return None

    def max_date(self):
        """
        Returns the latest date

        """

        dates = [
            ts.end_date('datetime') for ts in self
            if ts.dseries is not None]

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
                values.append(ts_tmp.tseries[ts_tmp.row_no(date)])
            except ValueError:
                if notify:
                    raise ValueError("ts %s does not have a value on %s" % (
                        idx, date))
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
            return self[1]

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
            if ts_tmp.key == '' or ts_tmp.key is None:
                raise ValueError(
                    "There must be a key for each timeseries.")

        return dict([(ts_tmp.key, ts_tmp) for ts_tmp in self])

    # def do_func(self, func, **kwargs):
    #    """
    #    This function accepts and **kwargs and runs that function on each
    #    timeseries in the list.

    #    This does not work yet due to final design incomplete.
    #    """

    #    for ts1 in self:
    #        ts1.do_func(func, kwargs)
