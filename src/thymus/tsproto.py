"""
This module implements the class Timeseries

"""

from copy import deepcopy
import numpy as np

from .constants import TS_ORDINAL, TS_TIMESTAMP, FREQ_DAYTYPES
from .constants import FREQ_IDAYTYPES, FREQ_D


class TsProto(object):
    """
    This class implements the low-level functions of the Timeseries class.

    By separating the these functions the code base can be broken into more
    managable chunks.

    Most of these functions are handed off the container functions in arrays.
    """

    def __init__(self):
        self.frequency = FREQ_D

        self.tseries = None
        self.dseries = None
        self.end_of_period = True

        self.key = ""
        self.columns = []

    def __iadd__(self, other):
        """ts += other"""
        return self._proc_func(new=False, func="__iadd__", other=other)

    def __irshift__(self, other):
        """'Return self>>=value."""
        return self._proc_func(new=False, func="__irshift__", other=other)

    def __iand__(self, other):
        """Return self&=value."""
        return self._proc_func(new=False, func="__iand__", other=other)

    def __isub__(self, other):
        """ts -= other"""
        return self._proc_func(new=False, func="__isub__", other=other)

    def __ifloordiv__(self, other):
        """ts /= other"""
        return self._proc_func(new=False, func="__ifloordiv__", other=other)

    def __ilshift__(self, other):
        """Return self<<=value."""
        return self._proc_func(new=False, func="__ilshift__", other=other)

    def __itruediv__(self, other):
        """ts /= other"""
        return self._proc_func(new=False, func="__itruediv__", other=other)

    def __imod__(self, other):
        """ts %= other"""
        return self._proc_func(new=False, func="__imod__", other=other)

    def __ior__(self, other):
        """Return self|=value."""
        return self._proc_func(new=False, func="__ior__", other=other)

    def __ixor__(self, other):
        """Return self^=value."""
        return self._proc_func(new=False, func="__ixor__", other=other)

    def __imul__(self, other):
        """ts *= other"""
        return self._proc_func(new=False, func="__imul__", other=other)

    def __ipow__(self, other):
        """ts **= other"""
        return self._proc_func(new=False, func="__ipow__", other=other)

    def __radd__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__radd__", other=other)

    def __rtruediv__(self, other):
        """Return other / ts."""
        return self._proc_func(new=True, func="__rtruediv__", other=other)

    def __rand__(self, other):
        """Return other & ts."""
        return self._proc_func(new=True, func="__rand__", other=other)

    def __rxor__(self, other):
        """Return value^self."""
        return self._proc_func(new=True, func="__rxor__", other=other)

    def __rdivmod__(self, other):
        """Return divmod(value, self)"""
        return self._proc_func(new=True, func="__rdivmod__", other=other)

    def __rmod__(self, other):
        """Return other % ts."""
        return self._proc_func(new=True, func="__rmod__", other=other)

    def __rmul__(self, other):
        """Return other * ts."""
        return self._proc_func(new=True, func="__rmul__", other=other)

    def __rfloordiv__(self, other):
        """Return value//self."""
        return self._proc_func(new=True, func="__rfloordiv__", other=other)

    def __rlshift__(self, other):
        """Return self<<value."""
        return self._proc_func(new=True, func="__rlshift__", other=other)

    def __rsub__(self, other):
        """Return other - ts."""
        return self._proc_func(new=True, func="__rsub__", other=other)

    def __ror__(self, other):
        """Return value|self"""
        return self._proc_func(new=True, func="__ror__", other=other)

    def __rpow__(self, other):
        """Return other ** ts."""
        return self._proc_func(new=True, func="__rpow__", other=other)

    def __rrshift__(self, other):
        """Return value>>self."""
        return self._proc_func(new=True, func="__rrshift__", other=other)

    def __abs__(self):
        """Return abs(ts)."""
        return self._proc_func(new=True, func="__abs__", other=None)

    def __pos__(self):
        """Return +ts."""
        return self._proc_func(new=True, func="__pos__", other=None)

    def __neg__(self):
        """Return -ts."""
        return self._proc_func(new=True, func="__neg__", other=None)

    def __invert__(self):
        """not ts."""
        return self._proc_func(new=True, func="__invert__", other=None)

    def __add__(self, other):
        """ts + other.

        Related functions:
            add()
        """
        return self._proc_func(new=True, func="__add__", other=other)

    def __pow__(self, other):
        """Return ts ** other."""
        return self._proc_func(new=True, func="__pow__", other=other)

    def __and__(self, other):
        """Return ts & other."""
        return self._proc_func(new=True, func="__and__", other=other)

    def __divmod__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__divmod__", other=other)

    def __eq__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__eq__", other=other)

    def __floordiv__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__floordiv__", other=other)

    def __ge__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__ge__", other=other)

    def __sub__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__sub__", other=other)

    def __truediv__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__truediv__", other=other)

    def __gt__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__gt__", other=other)

    def __xor__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__xor__", other=other)

    def __le__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__le__", other=other)

    def __rshift__(self, other):
        """Return self>>value."""
        return self._proc_func(new=True, func="__rshift__", other=other)

    def __lshift__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__lshift__", other=other)

    def __lt__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__lt__", other=other)

    def __mod__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__mod__", other=other)

    def __mul__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__mul__", other=other)

    def __ne__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__ne__", other=other)

    def __or__(self, other):
        """Return other + ts."""
        return self._proc_func(new=True, func="__or__", other=other)

    def _proc_func(self, new, func, other=None):
        """Processes container function.

        Reorganize this.
        """

        if new:
            tmp_ts = self.clone()

            if isinstance(other, TsProto):
                self._column_checks(tmp_ts, other)
                tmp_ts, other = self.common_length(tmp_ts, other)

            if other is None:
                # there may be others that should be in this list.
                #   at the moment, fixing a problem.
                if func in ("__eq__", "__ne__"):
                    tmp_ts.tseries = getattr(tmp_ts.tseries, func)(other)
                else:
                    tmp_ts.tseries = getattr(tmp_ts.tseries, func)()
            else:
                if isinstance(other, TsProto):
                    tmp_ts.tseries = getattr(tmp_ts.tseries, func)(
                        other.tseries
                    )
                else:
                    tmp_ts.tseries = getattr(tmp_ts.tseries, func)(other)

            return tmp_ts
        else:
            if other is None:
                self.tseries = (getattr(self.tseries, func)(),)
                return self
            else:
                if isinstance(other, TsProto):
                    self._column_checks(self, other)
                    self, other = self.common_length(self, other)
                    self.tseries = getattr(self.tseries, func)(other.tseries)
                else:
                    self.tseries = getattr(self.tseries, func)(other)
                return self

    @staticmethod
    def _column_checks(ts1, ts2):
        """
        This function raises an error if the columns on the two timeseries
        do not match.
        """
        status = False
        if len(ts1.tseries.shape) == 2 and len(ts2.tseries.shape) != 2:
            status = True
        elif len(ts1.tseries.shape) != 2 and len(ts2.tseries.shape) == 2:
            status = True

        elif len(ts1.tseries.shape) == 2 and len(ts2.tseries.shape) == 2:
            if ts1.tseries.shape[1] != ts2.tseries.shape[1]:
                status = True

        else:
            pass

        if status:
            raise ValueError(
                " ".join(
                    ["Both timeseries must have the same columns:", "%s vs %s"]
                )
                % (ts1.tseries.shape, ts2.tseries.shape)
            )

    @staticmethod
    def _array_size_check(ts1, ts2):
        """Raise error if timeseries' shapes do not match."""
        if np.array_equal(ts1, ts2):
            return True
        else:
            raise ValueError(
                " ".join(
                    ["Sizes of the timeseries are different:", "%s vs %s"]
                )
                % (ts1.tseries.shape, ts2.tseries.shape)
            )

    def make_arrays(self):
        """
        Convert the date and time series lists (if so) to numpy arrays
        """
        self.tseries = self._make_array(self.tseries, np.float64)

        if self.get_date_series_type() == TS_ORDINAL:
            self.dseries = self._make_array(self.dseries, np.int32).flatten()
        else:
            self.dseries = self._make_array(self.dseries, np.float64).flatten()

    @staticmethod
    def _make_array(convert_list, numtype):
        """
        Converts a list to numpy array
        """
        return np.array(convert_list, numtype)

    def lengths(self):
        """
        This function returns the lengths of both the date series and time
        series. Both numbers are included in case a mismatch has occurred.
        """
        return (len(self.dseries), len(self.tseries))

    def get_date_series_type(self):
        """
        This function returns the date series type associated with the
        timeseries.  The choices are TS_ORDINAL or TS_TIMESTAMP.

        """

        if self.frequency in FREQ_DAYTYPES:
            return TS_ORDINAL
        elif self.frequency in FREQ_IDAYTYPES:
            return TS_TIMESTAMP
        else:
            raise ValueError("Unknown frequency: %s" % self.frequency)

    def __getitem__(self, key):
        """
        This function returns a timeseries where both the date and values are
        sliced.

        Usage:
            ts[:10]

            returns a timeseries with dseries and tseries of length 10.

        """

        if isinstance(key, tuple):
            dkey = key[0]
        else:
            dkey = key

        tmp_ts = self.clone()
        tmp_ts.dseries = tmp_ts.dseries[dkey]
        tmp_ts.tseries = tmp_ts.tseries[key]

        return tmp_ts

    def clone(self):
        """This function returns a copy of the timeseries."""
        return deepcopy(self)

    @staticmethod
    def common_length(*ts):
        """
        This function trims the lengths of timeseries and returns all
        timeseries with the same length.

        The idea is that in order to do array operations there must be a
        common length for each timeseries.

        Reflecting the bias for using timeseries sorted from latest info to
        earlier info, truncation takes place at the end of the array. That
        way older less important values are removed if necessary.

        This function does not alter the timeseries passed in. The list of
        timeseries returned are clones of the originals.

        Changed:

        Usage:
            [ts1, ts2, ..., ts_n] = self.common_length(*ts)

        Formerly:
            ts1_new, ts2_new = self.common_length(ts1, ts2)


        """

        min_length = min([len(ts_tmp.tseries) for ts_tmp in ts])

        return [ts_tmp[:min_length] for ts_tmp in ts]

    def shape(self):
        """
        This function return the shape of the timeseries. This is a shortcut
        to putting in ts.tseries.shape.
        """

        if self.tseries is None:
            return None
        elif isinstance(self.tseries, list):
            return np.array(self.tseries).shape
        else:
            return self.tseries.shape

    def if_dseries_match(self, ts):
        """
        This function returns True if the date series are the same.
        """

        return np.array_equal(self.dseries, ts.dseries)

    def if_tseries_match(self, ts):
        """
        This function returns True if the time series are the same.
        """

        return np.array_equal(self.tseries, ts.tseries)
