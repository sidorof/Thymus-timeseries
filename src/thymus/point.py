# thymus/point.py
"""
This module implements the Point class.
"""


class Point(object):
    """
    This class enables a combined look at a specific point in a
    time series. While the purpose of Thymus-Timeseries is the
    separation of dates and values, there are times when having
    both together can be very useful.

    Usage:
    point = Point(ts, row)

    This produces an object:

    point.ts      a reference to the parent time series
    point.date    ordinal/timestamp
    point.values  an array of values

    If columns are being used for the object, properties
    are created for each column / value pair.

    For example:

    ts.columns = ["dog", "cat", "squirrel"]}

    Properties will have
        point.dog
        point.cat
        point.squirrel

    as well as values, as referenced above.

    Setting point.dog to a new value will update the column in
    ts.tseries[row].

    print(point)
    <Point: row_no: 3, date: 2020-01-04,
      dog: 0.8709958385754379
      cat: 0.9677731539727088
      squirrel: 1.0645504693699797 />

    """

    def __init__(self, ts, row_no):
        self.ts = ts
        self.row_no = row_no

        if len(self.ts.tseries.shape) == 2:
            shape = self.ts.tseries.shape
        else:
            shape = (self.ts.tseries.shape, 1)

        if ts.columns and len(ts.columns) == shape[1]:
            for idx, column in enumerate(ts.columns):

                def get_value(self, idx=idx):
                    return self.values[idx]

                get_value.__doc__ = f"Gets value from column {idx}."

                def set_value(self, value, idx=idx):
                    self.values[idx] = value

                set_value.__doc__ = f"Sets value in column {idx}."

                setattr(self.__class__, column, property(get_value, set_value))

    @property
    def values(self):
        """
        The values found at ts.tseries[row_no].

        These values cannot be changed directly. However, that is
        possible using the generated column variables.
        """
        return self.ts.tseries[self.row_no]

    @property
    def date(self):
        """The date found at ts.dseries[row_no]."""
        return self.ts.dseries[self.row_no]

    def __repr__(self, line_break=60):
        """
        If the line of column/values will be over 60 characters, the
        output will be vertical for easier viewing.
        """
        if len(self.ts.tseries.shape) == 1:
            # wrong shape
            if self.ts.columns:
                values = f"{self.ts.columns[0]}: {self.values}"
            else:
                values = self.values

        elif self.ts.columns:
            values = ", ".join(
                [
                    f"{column}: {value}"
                    for column, value in zip(self.ts.columns, self.values)
                ]
            )
            if len(values) > line_break:
                values = "\n  " + values.replace(", ", "\n  ")
        else:
            values = self.values

        sdate = self.date_str()
        name = self.__class__.__name__
        row_no = self.row_no
        return f"<{name}: row_no: {row_no}, date: {sdate}, {values} />"

    def date_str(self):
        """
        Returns the date in string format.
        """
        return self.ts.fmt_date(self.date, self.ts.get_date_series_type())

    def datetime(self):
        """
        Returns the date as a date/datetime object.
        """
        return self.ts.get_datetime(self.date)

    def to_dict(self, dt_fmt=None):
        """
        This function returns a dict of the point variables.

        Usage:
            to_dict(dt_fmt=None)

        Parameters:
            dt_fmt: (None|str) : Format choice is "str" or "datetime"

        Returns:
            point (dict)
        """

        pdict = {"row_no": self.row_no}

        if dt_fmt is None:
            pdict["date"] = self.date
        elif dt_fmt == "str":
            pdict["date"] = self.date_str()
        elif dt_fmt == "datetime":
            pdict["date"] = self.datetime()
        else:
            raise ValueError("Invalid dt_fmt: choices(None,str, datetime)")
        if self.ts.columns:
            tmp = dict(
                [
                    [column, value]
                    for column, value in zip(self.ts.columns, self.values)
                ]
            )

            pdict.update(tmp)
        return pdict
