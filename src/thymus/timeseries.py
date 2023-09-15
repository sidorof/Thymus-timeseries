"""
This module implements the class Timeseries

"""
import datetime as dt
from copy import deepcopy
import json
import numpy as np

from .constants import TS_ORDINAL, FREQ_D, FREQ_M
from .constants import TS_TIMESTAMP
from .constants import FREQ_DAYTYPES, FREQ_IDAYTYPES

from .freq_conversions import convert

from .tsproto import TsProto
from .point import Point

FMT_DATE = "%Y-%m-%d"
FMT_IDATE = "%Y-%m-%d %H:%M:%S"


class Timeseries(TsProto):
    """
    This class holds timeseries data. Dates and values are kept in
    separate numpy arrays.

    Usage:

        ts = Timeseries(
            frequency=FREQ_D,   defaults to daily
            dseries=None,       a numpy array with ordinal / timestamps
            tseries=None,       a numpy array of values
            end_of_period=True, did these values take place during the period?
            key='',             an optional key for naming the timeseries
            columns=None        optional columns for naming columns of the
                                values
        )
    """

    point_class = Point

    def __init__(
        self,
        frequency=FREQ_D,
        end_of_period=True,
        key="",
        columns=None,
        **kwargs,
    ):
        TsProto.__init__(self)

        self.frequency = frequency
        self.key = key

        if "tseries" in kwargs:
            self.tseries = kwargs.get("tseries", None)

        if "dseries" in kwargs:
            self.dseries = kwargs.get("dseries", None)

        self.end_of_period = end_of_period

        self.columns = columns

    def series_direction(self):
        """
        if a lower row is an earlier date, then 1 for ascending
        if a lower row is a later date then -1 for descending

        Related functions:
        reverse, sort_by_date
        """
        if self.dseries is not None:
            if len(self.dseries) > 1:
                if self.dseries[0] < self.dseries[-1]:
                    return 1
                else:
                    return -1
        return 0

    def start_date(self, fmt=None):
        """
        This function returns the starting date of the timeseries in its
        native value, timestamp or ordinal.

        If fmt is 'str' returns in string format
        If fmt is 'datetime' returns as datetime object

        CHANGE: this now returns
            a date object if ordinal
            a datetime if timestamp

        Note: look at consolidating return date formats:
            end_date, get_datetime
        """
        if self.dseries is None:
            return None
        if self.series_direction() == 1:
            row_no = 0
        else:
            row_no = -1

        if fmt is None:
            return self.dseries[row_no]
        elif fmt == "str":
            return self.fmt_date(
                self.dseries[row_no], dt_type=self.get_date_series_type()
            )
        elif fmt == "datetime":
            return self.get_datetime(self.dseries[row_no])
        else:
            raise ValueError("Invalid date format fmt: %s" % fmt)

    def end_date(self, fmt=None):
        """
        This funtcion returns the ending date of the timeseries in its native
        value, timestamp or ordinal.

        If fmt is 'str' returns in string format
        If fmt is 'datetime' returns as datetime object
        """
        if self.series_direction() == 1:
            row_no = -1
        else:
            row_no = 0

        if fmt is None:
            return self.dseries[row_no]
        elif fmt == "str":
            return self.fmt_date(
                self.dseries[row_no], dt_type=self.get_date_series_type()
            )
        elif fmt == "datetime":
            return self.get_datetime(self.dseries[row_no])
        else:
            raise ValueError("Invalid date format fmt: %s" % fmt)

    def get_datetime(self, date):
        """
        This function returns a date as a datetime object.
        This takes into account the type of date stored in dseries.

        Usage:
            self.get_datetime(date)
        """
        date_series_type = self.get_date_series_type()
        if date_series_type == TS_ORDINAL:
            return dt.date.fromordinal(date)
        # must be timestamp
        return dt.datetime.fromtimestamp(date)

    def to_dict(self, dt_fmt=None, data_list=False):
        """
        Returns the time series as a dict with the date as the key.

        Usage:
            self.to_dict(dt_fmt=None, data_list=False)

        This has been reworked to include all fields of the timeseries
        rather than just dates and times, so header informtion is now included.

        Also, for flexibility, the date can be formatted in various ways:
            dt_fmt=None       -- native format depending on frequency
                                 but converted to string
            dt_fmt='datetime' -- datetime objects
            dt_fmt='str'      -- converts dates to string using
                                 FMT_DATE or FMT_IDATE, depending on the
                                 timeseries type
        The boolean, data_list, signals whether dates should be used
        as keys in a dict for the values, or whether the dates and values
        are output as a list.

        This matters because some operations are necessary to target
        specific dates, but it does not preserve order. Or, if data_list
        is True, then the combination of dates and values are output as
        a list and order is maintained.

        """
        new_dict = {}
        new_dict["header"] = self.header()

        if dt_fmt is None:
            # native format, but converted to a string
            dseries = [str(date) for date in self.dseries.tolist()]
        elif dt_fmt == "datetime":
            dseries = self.datetime_series()
        elif dt_fmt == "str":
            dseries = self.date_string_series()
        else:
            raise ValueError("Unsupported dt_fmt: %s" % (dt_fmt))

        tseries = self.tseries.tolist()
        if data_list:
            data = [(dseries[i], tseries[i]) for i in range(len(self.tseries))]
        else:
            data = dict(
                [(dseries[i], tseries[i]) for i in range(len(self.tseries))]
            )

        new_dict["data"] = data

        return new_dict

    def from_dict(self, ts_dict):
        """
        This function accepts a dict and assembles a timeseries.

        Usage:
            self.from_dict(ts_dict)

        The dict must be:
            {
                "header": {
                     items
                 },
                "data": [
                    [date1, value1],
                    [date2, value2]
                ]
            }

        Or,
            {
                "header": {
                    items
                },
                "data": {
                    date1: values,
                    date2: values,
                }
            }

        The date formatting uses the same rules as creation in self.to_dict.

        If the data portion is a dict rather than a list, the timeseries is
        sorted in reverse data order by default.

        It loads in-place, but also returns self for use with chaining.
        """
        # header
        keys = list(ts_dict.keys())
        if "header" not in keys:
            raise ValueError(f"Missing header key 'header':  {keys}")
        if "data" not in keys:
            raise ValueError(f"Missing header key 'data':  {keys}")

        header = ts_dict["header"]
        for key, value in header.items():
            self.__setattr__(key, value)

        data = ts_dict["data"]

        do_sort = False
        if isinstance(data, dict):
            do_sort = True
            data = list(data.items())

        # dseries
        if self.get_date_series_type() == TS_ORDINAL:
            fmt = FMT_DATE
            self.dseries = [
                dt.datetime.strptime(item[0], fmt).toordinal() for item in data
            ]
        elif self.get_date_series_type() == TS_TIMESTAMP:
            fmt = FMT_IDATE
            self.dseries = [
                dt.datetime.strptime(item[0], fmt).timestamp() for item in data
            ]
        else:
            raise ValueError("undefined frequency: %s" % self.frequency)

        # tseries
        self.tseries = [item[1] for item in data]

        self.make_arrays()

        if do_sort:
            self.sort_by_date(reverse=True, force=True)

        return self

    def to_list(self):
        """Returns the timeseries as a list."""

        return [
            (str(self.dseries[i]), deepcopy(self.tseries[i]))
            for i in range(self.shape()[0])
        ]

    def to_json(self, indent=2, dt_fmt="str", data_list=True):
        """
        This function returns the timeseries in JSON format.

        Usage:
            self.as_json(indent=2, dt_fmt=str, data_list=True)

        dt_fmt options are the same as for to_dict

        """
        return json.dumps(
            self.to_dict(dt_fmt, data_list=data_list), indent=indent
        )

    def from_json(self, json_str):
        """
        This function loads a string in JSON format to inhabit a Timeseries
        object.

        Usage:
            self.from_json(json_str)

        It looks for a format similar to the following:
        {
            "header": {
                "end_of_period": True,
                "key": "",
                "columns": [],
                "frequency": "d"
            },
            "data": [
                ["2015-12-31", 0.0],
                ["2016-01-01", 1.0],
                ["2016-01-02", 2.0],
                ["2016-01-03", 3.0],
                ["2016-01-04", 4.0]
            ]
        }

        """
        tmpdict = json.loads(json_str)

        self.from_dict(tmpdict)

        return self

    def extend(self, ts, overlay=True):
        """
        This function combines a timeseries to another, taking into account the
        possibility of overlap.

        This assumes that the frequency is the same.

        This function is chiefly envisioned to extend a timeseries with
        additional dates.

        Usage:
            self.extend(ts, overlay=True)

        If overlay is True then the incoming timeseries will overlay
        any values that are duplicated.

        NOTE: add a check to prevent unwanted overlays
        """
        series_dir = self.series_direction()
        if series_dir == -1:
            reverse = True
        else:
            reverse = False

        self_dict = self.to_dict()["data"]
        ts_dict = ts.to_dict()["data"]

        for tdate in ts_dict.keys():
            if tdate in self_dict.keys():
                if overlay:
                    self_dict[tdate] = ts_dict[tdate]
                else:
                    raise ValueError(
                        "Duplicate dates, overlay parameter is False: %s"
                        % (tdate)
                    )
            else:
                self_dict[tdate] = ts_dict[tdate]

        self.dseries = []
        self.tseries = []
        for date, value in sorted(self_dict.items(), reverse=reverse):
            self.dseries.append(date)
            self.tseries.append(value)

        self.make_arrays()

    def add(self, ts, match=True):
        """
        Adds two timeseries together.

        if match is True:
            means there should be a one to one corresponding date in each time
            series.  If not raise error.
        else:
            means that timeseries with sporadic or missing dates can be added

        Note: this does not evaluate whether both timeseries have the same
                number of columns. It will fail if they do not.

        Returns the timeseries. Not in-place.
        """
        self._column_checks(self, ts)

        series_dir = self.series_direction()
        if series_dir == -1:
            reverse = True
        else:
            reverse = False

        self_ts = self.clone()
        tmp_ts = ts.clone()
        shape = tmp_ts.shape()
        if match:
            if len(self_ts.tseries) != len(tmp_ts.tseries):
                raise ValueError("Timeseries do not have the same length.")

            if self.if_dseries_match(ts) is False:
                raise ValueError("Dateseries do not have the same dates.")

            #   ok
            self_ts.tseries += tmp_ts.tseries
            return self_ts

        else:
            #   Dates do not have to match up. return an aglomeration of both
            dates = self_ts.to_dict()["data"]
            dates1 = tmp_ts.to_dict()["data"]

            if len(shape) > 1:
                # convert back to np arrays for the addition
                for key, value in list(dates.items()):
                    dates[key] = np.array(value)
                for key, value in list(dates1.items()):
                    dates1[key] = np.array(value)

            for pdate, value in dates1.items():
                if isinstance(value, float):
                    dates.setdefault(pdate, 0)
                else:
                    dates.setdefault(pdate, np.zeros(shape))
                dates[pdate] += value

            self_ts.dseries = []
            self_ts.tseries = []
            for date, value in sorted(dates.items(), reverse=reverse):
                self_ts.dseries.append(date)
                self_ts.tseries.append(value)

            self_ts.make_arrays()

            return self_ts

    def replace(self, ts, match=True):
        """
        This function replaces values where the dates match an incoming
        timeseries. So if the incoming date on the timeseries matches, the
        value in the current timeseries will be replaced by the incoming
        timeseries.

        Usage:
            self.replace(ts, match=True)

        If match is False, the incoming timseries may have dates not found in
        the self timeseries.

        Returns the modified timeseries. Not in place.

        """
        series_dir = self.series_direction()
        if series_dir == -1:
            reverse = True
        else:
            reverse = False

        self_ts = self.clone()
        tmp_ts = ts.clone()

        self_dates = self_ts.to_dict()["data"]
        ts_dates = tmp_ts.to_dict()["data"]

        if match:
            for date, value in ts_dates.items():
                if date in self_dates:
                    self_dates[date] = value

        else:
            for date, value in ts_dates.items():
                self_dates[date] = value

        self_ts.dseries = []
        self_ts.tseries = []
        for date, value in sorted(self_dates.items(), reverse=reverse):
            self_ts.dseries.append(date)
            self_ts.tseries.append(value)

        self_ts.make_arrays()

        return self_ts

    def combine(self, tss, discard=True, pad=None):
        """
        This function combines timeseries into a single array. Combining in
        this case means accumulating additional columns of information.

        Truncation takes place at the end of rows. So if the timeseries is
        sorted from latest dates to earliest dates, the older values would be
        removed.

        Usage:
            self.combine(tss, discard=True, pad=None)

        If discard:
            Will truncate all timeseries lengths down to the shortest
            timeseries.

        if discard is False
            an error will be raised if the all the lengths do not match

            unless:
                if pad is not None:
                    the shorter timeseries will be padded with the value pad.

        Returns the new ts.
        """
        series_dir = self.series_direction()
        if isinstance(tss, Timeseries):
            # A single, make into a list of timeseries
            tss = [tss]

        tss = [self.clone()] + [ts_tmp.clone() for ts_tmp in tss]
        for tmp_ts in tss:
            if len(tmp_ts.tseries.shape) == 1:
                tmp_ts.tseries = tmp_ts.tseries.reshape((-1, 1))

        # check lengths
        if discard is False:
            if pad is None:
                length = len(self.tseries)
                for tmp_ts in tss:
                    if length != len(tmp_ts.tseries):
                        raise ValueError("Lengths are not the same.")
            else:
                # get max length
                max_lens = [tmp_ts.tseries.shape[0] for tmp_ts in tss]
                max_len = max(max_lens)

                ts_ref = tss[max_lens.index(max_len)]
                ts_ref_len = ts_ref.tseries.shape[0]

                for i, tmp_ts in enumerate(tss):
                    tmp_ts = tss[i].clone()
                    ts_len = tmp_ts.tseries.shape[0]

                    # ready to pad
                    if ts_ref_len - ts_len > 0:
                        col_count = tmp_ts.tseries.shape[1]
                        pad_values = (
                            np.ones((ts_ref_len - ts_len, col_count)) * pad
                        )

                        # dates added to the end
                        if ts_len < max_len:
                            tmp_ts.tseries = np.append(
                                tmp_ts.tseries, pad_values
                            ).reshape((-1, col_count))
                            tmp_ts.dseries = np.append(
                                tmp_ts.dseries, ts_ref.dseries[ts_len:]
                            )

                        # put it back
                        tss[i] = tmp_ts
        else:
            length = min([len(tmp_ts.tseries) for tmp_ts in tss])
            for tmp_ts in tss:
                tmp_ts.trunc(finish=length)

        # all timeseries same length
        base_ts = tss[0]
        base_ts.tseries = np.hstack([ts_tmp.tseries for ts_tmp in tss])

        # force a sort
        if series_dir == 1:
            base_ts.sort_by_date(force=True)
        else:
            base_ts.sort_by_date(reverse=True, force=True)
        return base_ts

    def date_string_series(self, dt_fmt=None):
        """
        This function returns a list of the dates in the timeseries as
        strings.

        Usage:
            self.date_string_series(dt_fmt=None)

        dt_fmt is a datetime mask to alter the default formatting.
        """
        dt_type = self.get_date_series_type()
        if dt_fmt is None:
            # use default
            if dt_type == TS_ORDINAL:
                dt_fmt = FMT_DATE
            else:
                dt_fmt = FMT_IDATE

        return [self.fmt_date(date, dt_type, dt_fmt) for date in self.dseries]

    def sort_by_date(self, reverse=False, force=False):
        """
        This function converts a timeseries to either date order or reverse
        date order.

        Usage:
            sort_by_date(self, reverse=False, force=False)

        If reverse is True, then order will be newest to oldest.
        If force is False, the assumption is made that comparing the first
        and last date will determine the current order of the timeseries. That
        would mean that unnecessary sorting can be avoided. Also, if the order
        needs to be reversed, the sort is changed via the less expensive
        reverse function.

        If dates and values are in no particular order, with force=True, the
        actual sort takes place.

        This function changes the data in-place.
        """
        if force:
            dseries = []
            tseries = []
            for date, values in sorted(
                self.to_dict()["data"].items(), reverse=reverse
            ):
                dseries.append(date)
                tseries.append(values)
            self.dseries = dseries
            self.tseries = tseries
            self.make_arrays()

        else:
            if reverse is False and self.series_direction() == 1:
                # unnecessary
                pass
            elif reverse is True and self.series_direction() == -1:
                # unnecessary
                pass
            else:
                self.reverse()

    def reverse(self):
        """
        This function does in-place reversal of the timeseries and dateseries.
        """
        if len(self.tseries.shape) == 1:
            self.tseries = self.tseries[::-1]
        else:
            self.tseries = np.flipud(self.tseries)

        self.dseries = self.dseries[::-1]

    def convert(self, new_freq, include_partial=True, **kwargs):
        """
        This function returns the timeseries converted to another frequency,
        such as daily to monthly.

        Usage:
            convert(new_freq, include_partial=True, **kwargs)

        The only kwarg is
            weekday=<some value>

        This is used when converting to weekly data. The weekday number
        corresponds to the the datetime.weekday() function.
        """
        if new_freq not in FREQ_IDAYTYPES + FREQ_DAYTYPES:
            raise ValueError("Invalid new frequency: %s" % new_freq)

        if self.frequency == new_freq:
            return self

        return convert(
            self, new_freq, include_partial=include_partial, **kwargs
        )

    def get_diffs(self):
        """
        This function gets the differences between values from date to date
        in the timeseries.
        """
        series_dir = self.series_direction()

        tmp_ts = self.clone()
        if series_dir == 1:
            tmp_ts.reverse()

        tmp_ts.tseries = tmp_ts.tseries[:-1] - tmp_ts.tseries[1:]
        tmp_ts.dseries = tmp_ts.dseries[:-1]

        if series_dir == 1:
            tmp_ts.reverse()

        return tmp_ts

    def get_pcdiffs(self):
        """
        This function gets the percent differences between values in the
        timeseries.

        No provision for dividing by zero here.
        """
        series_dir = self.series_direction()

        tmp_ts = self.clone()

        if series_dir == 1:
            tmp_ts.reverse()

        tmp_ts.tseries = (
            (tmp_ts.tseries[:-1] / tmp_ts.tseries[1:]) - 1.0
        ) * 100.0
        tmp_ts.dseries = tmp_ts.dseries[:-1]

        if series_dir == 1:
            tmp_ts.reverse()

        return tmp_ts

    def items(self, fmt=None):
        """This function returns the date series and the time series as if it
        is in one list. The term items used to suggest the iteration of dicts
        where items are the key, value combination.

        if fmt == 'str':
            the dates are output as strings
        """
        if fmt == "str":
            return [
                (date, value.tolist())
                for date, value in zip(self.date_string_series(), self.tseries)
            ]
        else:
            return [
                (date, value)
                for date, value in zip(self.datetime_series(), self.tseries)
            ]

    def get_point(self, rowdate=None, row_no=None):
        """
        This function gets both date and timeseries values for a particular
        row. It packages the results into an object. If the timeseries uses
        columns, those column names become object attributes.

        This should be viewed as a window into a particular row. Updating the
        point values updates the timeseries row values.

        Changing the row number on the point automatically updates the point
        for the new values.

        A point object can therefore be used in an interation of timeseries as
        part of an updating process.

        Usage:
            get_point(rowdate=None, row_no=None)

        Parameters:
            rowdate: (None|int|float|datetime) : As with ts.row_no,
                the date can be either the ordinal/timestamp or datetime
                object.
            row_no: (None:int) : The row number of the timeseries.

            Either a rowdate or row_no must be selected.

        Returns:
            point : (object) : Object of Point class

        """
        if rowdate:
            return self.point_class(self, self.row_no(rowdate=rowdate))

        if row_no is not None:
            return self.point_class(self, row_no)

        raise ValueError("Must use parameter 'rowdate' or 'row_no'")

    def trunc(self, start=None, finish=None, new=False):
        """
        This function truncates in place, typically.

        truncate from (start:finish)
        remember start is lowest number, latest date

        This truncation works on the basis of slicing, so
        finish is not inclusive.

        Usage:
            self.trunc(start=None, finish=None, new=False)

        If new is True, the timeseries will not be modified in place. Rather
        a new timeseries will be returned instead.
        """
        if new:
            tmp_ts = self.clone()
        else:
            tmp_ts = self

        if start and finish:
            tmp_ts.tseries = tmp_ts.tseries[start:finish]
            tmp_ts.dseries = tmp_ts.dseries[start:finish]
        elif start:
            tmp_ts.tseries = tmp_ts.tseries[start:]
            tmp_ts.dseries = tmp_ts.dseries[start:]
        elif finish:
            tmp_ts.tseries = tmp_ts.tseries[:finish]
            tmp_ts.dseries = tmp_ts.dseries[:finish]

        if new:
            return tmp_ts

    def truncdate(self, start=None, finish=None, new=False):
        """

        This function truncates in place on the basis of dates.

        Usage:
            self.truncdate(start=None, finish=None, new=False)

        start and finish are dates, input as either datetime or the actual
        internal format of the dseries (ordinals or timestamps).

        If the dates are not actually in the list, the starting date will
        be the next viable date after the start date requested. If the finish
        date is not available, the previous date from the finish date will be
        the last.

        If new is True, the timeseries will not be modified in place. Rather
        a new timeseries will be returned instead.
        """
        if isinstance(start, list) or isinstance(start, tuple):
            start, finish = start

        series_dir = self.series_direction()
        if series_dir == -1:
            self.reverse()

        if new:
            tmp_ts = self.clone()

        if start and finish:
            start = min(start, finish)
            finish = max(start, finish)

            start_row = self.row_no(start, closest=1)
            finish_row = self.row_no(finish, closest=-1)

            if new:
                tmp_ts = self[start_row : finish_row + 1]
            else:
                self.trunc(start=start_row, finish=finish_row + 1)

        elif start:
            # test if date exists
            start_row = self.row_no(start, closest=1)

            if new:
                tmp_ts = self[start_row:]
            else:
                self.trunc(start=start_row)

        elif finish:
            finish_row = self.row_no(finish, closest=-1)

            if new:
                tmp_ts = self[: finish_row + 1]
            else:
                self.trunc(finish=finish_row + 1)

        if series_dir == -1:
            self.reverse()
            if new:
                tmp_ts.reverse()

        if new:
            return tmp_ts

    def row_no(self, rowdate, closest=0, no_error=False):
        """
        Shows the row in the timeseries

        Usage:
            ts.row_no(rowdate=<datetime>)
            ts.row_no(rowdate=<date as either ordinal or timestamp>)

        Returns an error if the date is not found in the index

        if closest is invoked:
            closest = 1
                find the closest date after the rowdate
            closest = -1
                find the closest date before the rowdate

        If no_error
            returns -1 instead of raising an error if the date was
            outside of the timeseries.
        """
        row_error = -1

        series_dir = self.series_direction()

        if isinstance(rowdate, dt.datetime) or isinstance(rowdate, dt.date):
            rdate = self.date_native(rowdate)
        else:
            # assume it is appropriate
            rdate = rowdate

        if closest not in [-1, 0, 1]:
            raise ValueError("Invalid closest value: %s" % (closest))

        if closest == 0:
            selected = np.argwhere(self.dseries == rdate)

            if selected.shape[0] == 0:
                if no_error:
                    row_no = row_error
                else:
                    raise ValueError(
                        "%s not found in %s timeseries" % (rowdate, self.key)
                    )
            else:
                row_no = selected[0][0]

        elif closest == -1:
            selected = np.argwhere(self.dseries <= rdate)

            if selected.shape[0] == 0:
                if no_error:
                    row_no = row_error
                else:
                    raise ValueError(
                        "%s not found in %s timeseries" % (rowdate, self.key)
                    )

            if series_dir == 1:
                row_no = selected.max()
            else:
                row_no = selected.min()

        else:
            selected = np.argwhere(self.dseries >= rdate)

            if selected.shape[0] == 0:
                if no_error:
                    row_no = row_error
                else:
                    raise ValueError(
                        "%s not found in %s timeseries" % (rowdate, self.key)
                    )

            if series_dir == 1:
                row_no = selected.min()
            else:
                row_no = selected.max()

        return row_no

    def datetime_series(self):
        """
        This function returns the dateseries converted to a series of
        datetime objects.
        """
        if self.get_date_series_type() == TS_ORDINAL:
            return [dt.date.fromordinal(int(i)) for i in self.dseries]
        elif self.get_date_series_type() == TS_TIMESTAMP:
            return [dt.datetime.fromtimestamp(int(i)) for i in self.dseries]
        else:
            raise ValueError("timeseries must have a defined frequency")

    @staticmethod
    def fmt_date(numericdate, dt_type, dt_fmt=None):
        """
        This static method accepts a date and converts it to
        the format used in the timeseries.
        """
        if dt_type == TS_ORDINAL:
            if dt_fmt is None:
                dt_fmt = FMT_DATE
            return dt.date.fromordinal(int(numericdate)).strftime(dt_fmt)
        elif dt_type == TS_TIMESTAMP:
            if dt_fmt is None:
                dt_fmt = FMT_IDATE
            return dt.datetime.fromtimestamp(numericdate).strftime(dt_fmt)
        else:
            raise ValueError("Unknown dt_type: %s" % dt_type)

    def __repr__(self):
        """
        This function returns a representation of the class.
        """
        output = "\n".join(
            [
                f"<{self.__class__.__name__}>",
                f"key: {self.key}",
                f"columns: {self.columns}",
                f"frequency: {self.frequency}",
                f"daterange: {str(self.daterange('str'))}",
                f"end-of-period: {self.end_of_period}",
                f"shape: {str(self.shape())}",
            ]
        )

        return output

    def set_zeros(self, fmt=None, new=False):
        """
        This function converts an existing timeseries to zeros using the same
        shape as the existing timeseries.

        It is used as a convenience to create an empty timeseries with a
        specified date range.

        if fmt use as shape

        usage:
            set_zeros(self, fmt=None, new=False)
        """
        if new:
            tmp_ts = self.clone()
        else:
            tmp_ts = self

        if fmt is not None:
            tmp_ts.tseries = np.zeros(fmt)
        else:
            tmp_ts.tseries = np.zeros(tmp_ts.tseries.shape)

        if new:
            return tmp_ts

    def set_ones(self, fmt=None, new=False):
        """
        This function converts an existing timeseries to ones using the same
        shape as the existing timeseries.

        It is used as a convenience to create an empty timeseries with a
        specified date range.

        If fmt use as shape

        usage:
            set_ones(self, fmt=None, new=False)
        """
        if new:
            tmp_ts = self.clone()
        else:
            tmp_ts = self

        if fmt is not None:
            tmp_ts.tseries = np.ones(fmt)
        else:
            tmp_ts.tseries = np.ones(tmp_ts.tseries.shape)

        if new:
            return tmp_ts

    def header(self):
        """
        This function returns a dict of the non-timeseries data.

        Changed:
        Non-timeseries data is determined as an element of __dict__ that is
        not tseries or dseries.

        This enables more descriptive data to be included in the header.
        """
        return dict(
            [
                (key, value)
                for key, value in self.__dict__.items()
                if key not in ["tseries", "dseries"]
            ]
        )

    def date_native(self, date):
        """
        This awkwardly named function returns a date in the native format of
        of the timeseries, namely ordinal or timestamp.
        """
        if isinstance(date, dt.datetime) or isinstance(date, dt.date):
            datetype = self.get_date_series_type()

            if datetype == TS_ORDINAL:
                ndate = date.toordinal()
            else:
                ndate = date.timestamp()

            return ndate
        else:
            raise ValueError("date must be a datetime")

    def daterange(self, fmt=None):
        """
        This function returns the starting and ending dates of the timeseries.

        Usage:

            self.daterange()
                (735963, 735972)

            self.daterange('str')
                ('2015-12-31', '2016-01-09')

            self.daterange('datetime')
                (datetime(2015, 12, 31, 0, 0),
                 datetime.datetime(2016, 1, 9, 0, 0))

        """

        if self.dseries is not None:
            start_date, end_date = (self.dseries.min(), self.dseries.max())
        else:
            return (None, None)

        if fmt == "str":
            dt_type = self.get_date_series_type()
            start_date = self.fmt_date(start_date, dt_type)
            end_date = self.fmt_date(end_date, dt_type)
        elif fmt == "datetime":
            start_date = self.get_datetime(start_date)
            end_date = self.get_datetime(end_date)
        elif fmt is None:
            #   either timestamp or ordinal, pass through as is
            pass
        else:
            raise ValueError("Invalid fmt type: %s" % (fmt))

        return (start_date, end_date)

    def years(self, include_partial=True):
        """
        This function provides a quick way to summarize yearly data.

        It is basically a pass-through to the convert function with more
        decoration of the years.

        Usage:

            years(include_partial=True)

            returns a dict with year as keys
        """
        ts_years = convert(
            self, new_freq=FREQ_M, include_partial=include_partial
        )

        year_dict = {}

        tseries = ts_years.tseries
        dseries = ts_years.dseries

        for i in range(tseries.shape[0]):
            year = ts_years.get_datetime(dseries[i]).year
            year_dict[year] = tseries[i]

        return year_dict

    def months(self, include_partial=True):
        """
        This function provides a quick way to summarize monthly data.

        It is basically a pass-through to the convert function with more
        decoration of the months.

        Usage:

            months(include_partial=True)

            returns a dict with year-month as keys
        """
        ts_months = convert(
            self, new_freq=FREQ_M, include_partial=include_partial
        )

        month_dict = {}

        tseries = ts_months.tseries
        dseries = ts_months.dseries

        for i in range(tseries.shape[0]):
            date = ts_months.get_datetime(dseries[i])
            month = "%s-%02d" % (date.year, date.month)

            month_dict[month] = tseries[i]

        return month_dict

    def closest_date(self, rowdate, closest=1):
        """
        This function is a variation on the self.row_no function. The date
        presumably is not going to be found in the date series. Instead,
        given the parameter of closest, it eithers to either a row to the past
        or the future.

        Usage:
            self.closest_date(rowdate=date)             search forward
            self.closest_date(rowdate=date, closest=1)  search forward
            self.closest_date(rowdate=date, closest=-1) search backwards
        """
        row_no = self.row_no(rowdate=rowdate, closest=closest)

        return self.dseries[row_no]

    def get_duped_dates(self):
        """
        This function pulls dates that are duplicated. This is to be used to
        locate timeseries that are faulty.

        Usage:
            get_duped_dates()

            returns [[odate1, count], [odate2, count]]
        """
        dict_dates = {}

        for odate in self.dseries:
            dict_dates.setdefault(odate, 0)
            dict_dates[odate] += 1

        return [
            [odate, count] for odate, count in dict_dates.items() if count > 1
        ]

    def get_fromDB(self, **kwargs):
        """
        This is just a stub to suggest a viable name for getting data from
        a database.
        """
        pass

    def save_toDB(self, **kwargs):
        """
        This is just a stub to suggest a viable name for saving data to a
        database.
        """
        pass
