"""
This module tests the implementation of the timeseries class.
"""

from datetime import date, datetime, timedelta
import json
import numpy as np

import unittest

from src.constants import FREQ_SEC, FREQ_M
from src.timeseries import Timeseries, TS_TIMESTAMP, TS_ORDINAL


class TestTimeseries(unittest.TestCase):
    """This class tests the base class of Timeseries."""

    def setUp(self):
        # three timeseries
        self.ts = Timeseries()
        self.ts.key = "Test Key"
        self.ts.columns = ["F1"]

        start_date = datetime(2015, 12, 31).toordinal()
        self.ts.dseries = start_date + np.arange(10)
        self.ts.tseries = np.arange(10)
        self.ts.make_arrays()

        # longer timeseries
        self.ts_long = Timeseries()
        start_date = datetime(2015, 12, 31).toordinal()
        self.ts_long.dseries = start_date + np.arange(20)
        self.ts_long.tseries = np.arange(20)
        self.ts_long.make_arrays()

        # shorter timeseries
        self.ts_short = Timeseries()
        start_date = datetime(2015, 12, 31).toordinal()
        self.ts_short.dseries = start_date + np.arange(5)
        self.ts_short.tseries = np.arange(5)
        self.ts_short.make_arrays()

        # timeseries with multiple columns
        self.ts_mult = Timeseries()
        self.ts_mult.key = "ts_mult_key"
        start_date = datetime(2015, 12, 31).toordinal()
        self.ts_mult.dseries = start_date + np.arange(5)
        self.ts_mult.tseries = np.arange(10).reshape((5, 2))
        self.ts_mult.make_arrays()

    def test_class_init_(self):
        """Test class initialization."""
        tmp_ts = Timeseries()

        # this may change back to lists
        # self.assertIsInstance(tmp_ts.dseries, list)
        # self.assertIsInstance(tmp_ts.tseries, list)
        self.assertIsNone(tmp_ts.columns)
        self.assertEqual(tmp_ts.frequency, "d")

        # no particular error checking on frequency values
        # however, will fail during frequency conversions
        tmp_ts = Timeseries("m")

        self.assertEqual(tmp_ts.frequency, "m")

        # no tseries, dseries
        ts = Timeseries(dseries=np.arange(10), tseries=np.arange(10))

        self.assertListEqual(ts.tseries.tolist(), np.arange(10).tolist())
        self.assertListEqual(ts.dseries.tolist(), np.arange(10).tolist())

    @unittest.skip
    def test_setup(self):
        """Attempts to prove numpy arrays are created."""
        # should be numpy arrays
        # figure out the problem here
        self.assertIsInstance(self.ts.tseries, np.array)
        self.assertIsInstance(self.ts.dseries, np.array)

    def test_timeseries_series_direction(self):
        """Tests series direction flags."""
        # -1 or +1
        self.assertEqual(self.ts.series_direction(), 1)

        self.ts.reverse()
        self.assertEqual(self.ts.series_direction(), -1)

        # one row timeseries
        ts = Timeseries(dseries=[1], tseries=[1])

        self.assertEqual(ts.series_direction(), 0)

    def test_timeseries_start_date(self):
        """Tests start date regardless of date sorts and types."""
        # get as ordinal
        self.assertEqual(self.ts.dseries[0], self.ts.start_date())

        # reverse - now new to old
        self.ts.reverse()
        self.assertEqual(self.ts.dseries[-1], self.ts.start_date())

        # get as datetime from ordinal
        self.assertEqual(date(2015, 12, 31), self.ts.start_date("datetime"))

        # get as timestamp
        ts = Timeseries(frequency="sec")

        self.assertEqual("timestamp", ts.get_date_series_type())

        ts.dseries = datetime(2015, 12, 31).timestamp() + np.arange(10)
        ts.tseries = np.arange(10)

        self.assertEqual(ts.dseries[0], ts.start_date())

        # reverse - now new to old
        ts.reverse()
        self.assertEqual(ts.dseries[-1], ts.start_date())

        # get as datetime from timestamp
        self.assertEqual(date(2015, 12, 31), self.ts.start_date("datetime"))

        # string date
        self.assertEqual(self.ts.start_date("str"), "2015-12-31")

        # bad format
        self.assertRaises(ValueError, self.ts.start_date, "bad")

    def test_timeseries_end_date(self):
        """Tests end date regardless of date sorts and types."""

        # get as ordinal
        self.assertEqual(self.ts.dseries[-1], self.ts.end_date())

        # reverse - now new to old
        self.ts.reverse()
        self.assertEqual(self.ts.dseries[0], self.ts.end_date())

        # get as datetime from ordinal
        self.assertEqual(date(2016, 1, 9), self.ts.end_date("datetime"))

        # get as timestamp
        ts = Timeseries(frequency="sec")

        self.assertEqual("timestamp", ts.get_date_series_type())

        ts.dseries = datetime(2015, 12, 31, 0, 0, 0).timestamp() + np.arange(
            10
        )
        ts.tseries = np.arange(10)

        self.assertEqual(ts.dseries[-1], ts.end_date())

        # reverse - now new to old
        ts.reverse()
        self.assertEqual(ts.dseries[0], ts.end_date())

        # get as datetime from timestamp
        self.assertEqual(
            datetime(2015, 12, 31, 0, 0, 9), ts.end_date("datetime")
        )

        # string date
        self.assertEqual(self.ts.end_date("str"), "2016-01-09")

        # bad format
        self.assertRaises(ValueError, self.ts.end_date, "bad")

    def test_timeseries_get_datetime(self):
        """Tests conversion to datetime from ordinal/timestamps"""

        tmp_date = self.ts.start_date()

        self.assertEqual(date(2015, 12, 31), self.ts.get_datetime(tmp_date))

        ts = Timeseries(frequency="sec")

        ts.dseries = datetime(2015, 12, 31).timestamp() + np.arange(10)
        ts.tseries = np.arange(10)

        tmp_date = self.ts.start_date()
        self.assertEqual(date(2015, 12, 31), self.ts.get_datetime(tmp_date))

    def test_timeseries_to_dict(self):
        """Tests conversion of dates and values to a dict."""
        tdict = self.ts.to_dict()

        self.assertDictEqual(
            tdict["data"],
            {
                "735963": 0.0,
                "735964": 1.0,
                "735965": 2.0,
                "735966": 3.0,
                "735967": 4.0,
                "735968": 5.0,
                "735969": 6.0,
                "735970": 7.0,
                "735971": 8.0,
                "735972": 9.0,
            },
        )

        # NOTE: to_dict: needs test for datetime series
        # NOTE: 'to_dict: needs test for string dates

    def test_header(self):
        """Tests whether header data is complete."""

        ts = Timeseries(
            key="test",
            columns=["this", "is", "a", "test"],
            frequency="d",
            end_of_period=True,
        )

        self.assertDictEqual(
            ts.header(),
            {
                "key": "test",
                "columns": ["this", "is", "a", "test"],
                "frequency": "d",
                "end_of_period": True,
            },
        )

        # add extraneous descriptive data
        ts = Timeseries(
            key="test",
            columns=["this", "is", "a", "test"],
            frequency="d",
            end_of_period=True,
        )
        ts.description = "Here is a description of the timeseries."

        self.assertDictEqual(
            ts.header(),
            {
                "key": "test",
                "columns": ["this", "is", "a", "test"],
                "frequency": "d",
                "end_of_period": True,
                "description": "Here is a description of the timeseries.",
            },
        )

    def test_timeseries_to_list(self):
        """Tests conversion of dates and values to a list."""

        tlist = self.ts.to_list()

        self.assertListEqual(
            tlist,
            [
                ("735963", 0.0),
                ("735964", 1.0),
                ("735965", 2.0),
                ("735966", 3.0),
                ("735967", 4.0),
                ("735968", 5.0),
                ("735969", 6.0),
                ("735970", 7.0),
                ("735971", 8.0),
                ("735972", 9.0),
            ],
        )

    def test_timeseries_to_json(self):
        """
        Tests conversion of dates and values to json format.

        """
        # NOTE: to_json: only one example tested

        json_test = self.ts_mult.to_json(dt_fmt="str")

        self.maxDiff = None

        self.assertDictEqual(
            json.loads(json_test)["header"],
            {
                "end_of_period": True,
                "key": "ts_mult_key",
                "columns": None,
                "frequency": "d",
            },
        )

        self.assertListEqual(
            json.loads(json_test)["data"],
            [
                ["2015-12-31", [0.0, 1.0]],
                ["2016-01-01", [2.0, 3.0]],
                ["2016-01-02", [4.0, 5.0]],
                ["2016-01-03", [6.0, 7.0]],
                ["2016-01-04", [8.0, 9.0]],
            ],
        )

    def test_timeseries_from_json(self):
        """
        Tests loading a json formatted string to a timeseries object.

        """
        # NOTE: from_json: only one example tested
        json_test = """
            {
                "data": [
                    ["2015-12-31", [0.0, 1.0]],
                    ["2016-01-01", [2.0, 3.0]],
                    ["2016-01-02", [4.0, 5.0]],
                    ["2016-01-03", [6.0, 7.0]],
                    ["2016-01-04", [8.0, 9.0]]
                ],
                "header": {
                    "key": "test_key",
                    "columns": ["test"],
                    "frequency": "d",
                    "end_of_period": true
                }
            }
        """

        ts_tmp = Timeseries()

        ts_tmp.from_json(json_test)

        # header
        self.assertEqual(ts_tmp.key, "test_key")
        self.assertListEqual(ts_tmp.columns, ["test"])
        self.assertEqual(ts_tmp.frequency, "d")
        self.assertTrue(ts_tmp.end_of_period)

        # dseries
        self.assertListEqual(
            ts_tmp.date_string_series(),
            [
                "2015-12-31",
                "2016-01-01",
                "2016-01-02",
                "2016-01-03",
                "2016-01-04",
            ],
        )

        self.assertListEqual(
            ts_tmp.tseries.tolist(),
            [
                [0.0, 1.0],
                [2.0, 3.0],
                [4.0, 5.0],
                [6.0, 7.0],
                [8.0, 9.0],
            ],
        )

    def test_timeseries_extend(self):
        """Tests adding rows to a timeseries."""

        # create overlapping timeseries
        ts = Timeseries()
        start_date = datetime(2016, 1, 5).toordinal()
        ts.dseries = start_date + np.arange(10)
        ts.tseries = np.arange(10, 20)
        ts.make_arrays()

        ts_copy = self.ts.clone()

        self.assertRaises(ValueError, self.ts.extend, ts, overlay=False)

        # [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9.]
        #
        #                     [ 10. 11. 12. 13. 14. 15.  16.  17.  18.  19.]

        ts_copy.extend(ts, overlay=True)

        self.assertEqual(ts_copy.tseries[4], 4)
        self.assertEqual(ts_copy.tseries[5], 10)
        self.assertEqual(ts_copy.tseries[6], 11)
        self.assertEqual(ts_copy.tseries[7], 12)
        self.assertEqual(ts_copy.tseries[8], 13)
        self.assertEqual(ts_copy.tseries[9], 14)
        self.assertEqual(ts_copy.tseries[10], 15)
        self.assertEqual(ts_copy.tseries[11], 16)

    def test_timeseries_add(self):
        """Tests adding values to a timeseries."""

        # add same length
        ts = self.ts.clone()

        ts_new = self.ts.add(ts)

        # [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9.]
        self.assertEqual(ts_new.tseries[0], 0)
        self.assertEqual(ts_new.tseries[1], 2)
        self.assertEqual(ts_new.tseries[2], 4)
        self.assertEqual(ts_new.tseries[3], 6)
        self.assertEqual(ts_new.tseries[4], 8)

        self.assertEqual(ts_new.shape(), self.ts.shape())

        # add different length -- match True
        # [ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9.]

        # default is match=True
        self.assertRaises(ValueError, self.ts.add, self.ts_short)

        self.assertRaises(ValueError, self.ts.add, self.ts_short, match=True)

        # add different length -- match False
        ts_new = self.ts.add(self.ts_short, match=False)

        self.assertEqual(ts_new.tseries[0], 0)
        self.assertEqual(ts_new.tseries[1], 2)
        self.assertEqual(ts_new.tseries[2], 4)
        self.assertEqual(ts_new.tseries[3], 6)
        self.assertEqual(ts_new.tseries[4], 8)
        self.assertEqual(ts_new.tseries[5], 5)
        self.assertEqual(ts_new.tseries[6], 6)

        # add timeseries with more than one column
        ts_new = ts_new.combine(ts_new)
        ts_new1 = ts_new.add(ts_new)

        self.assertListEqual(
            ts_new1.tseries.tolist(),
            [
                [0.0, 0.0],
                [4.0, 4.0],
                [8.0, 8.0],
                [12.0, 12.0],
                [16.0, 16.0],
                [10.0, 10.0],
                [12.0, 12.0],
                [14.0, 14.0],
                [16.0, 16.0],
                [18.0, 18.0],
            ],
        )

    def test_timeseries_replace(self):
        """Tests replacing values in a timeseries."""

        ts = self.ts_short.clone()
        ts.tseries = ts.tseries**2

        ts_new = self.ts.replace(ts)

        self.assertEqual(ts_new.tseries[0], 0)
        self.assertEqual(ts_new.tseries[1], 1)
        self.assertEqual(ts_new.tseries[2], 4)
        self.assertEqual(ts_new.tseries[3], 9)
        self.assertEqual(ts_new.tseries[4], 16)
        self.assertEqual(ts_new.tseries[5], 5)
        self.assertEqual(ts_new.tseries[6], 6)
        self.assertEqual(ts_new.tseries[7], 7)
        self.assertEqual(ts_new.tseries[8], 8)
        self.assertEqual(ts_new.tseries[9], 9)

    def test_timeseries_combine_1(self):
        """A batch of tests adding columns to a timeseries."""

        # combine(self, tss, discard=True, pad=None)
        ts = self.ts.clone()
        # combine with defaults
        ts_new = self.ts.combine(ts)

        self.assertEqual(ts_new.tseries.shape[0], ts.tseries.shape[0])
        self.assertEqual(ts_new.tseries.shape[1], 2)

        for i in range(len(ts_new.tseries)):
            self.assertEqual(ts_new.tseries[i][1], i)

        # combine with the same length

        ts_new = self.ts.combine(ts)

        self.assertEqual(ts_new.tseries.shape[0], ts.tseries.shape[0])
        self.assertEqual(ts_new.tseries.shape[1], 2)

        for i in range(len(ts_new.tseries)):
            self.assertEqual(ts_new.tseries[i][1], i)

        # combine list of timeseries with the same length
        ts1 = self.ts.clone()
        ts_new = self.ts.combine([ts, ts1])

        self.assertEqual(ts_new.tseries.shape[0], ts.tseries.shape[0])
        self.assertEqual(ts_new.tseries.shape[1], 3)

        for i in range(len(ts_new.tseries)):
            self.assertEqual(ts_new.tseries[i][1], i)
            self.assertEqual(ts_new.tseries[i][2], i)

        # combine with shorter timeseries discard=True
        ts_short = self.ts_short.clone()

        ts_new = self.ts.combine(ts_short, discard=True)

        self.assertEqual(ts_new.tseries.shape[0], ts_short.tseries.shape[0])
        self.assertEqual(ts_new.tseries.shape[1], 2)

        for i in range(len(ts_new.tseries)):
            self.assertEqual(ts_new.tseries[i][1], i)

        # combine with shorter timeseries discard=False pad=None
        self.assertRaises(
            ValueError, ts.combine, ts_short, discard=False, pad=None
        )

        # combine with shorter timeseries discard=False pad=0
        ts_new = self.ts.combine(ts_short, discard=False, pad=0)

        self.assertEqual(ts_new.tseries.shape[0], self.ts.tseries.shape[0])
        self.assertEqual(ts_new.tseries.shape[1], 2)

        for i in range(len(ts_new.tseries)):
            if i < len(ts_short.tseries):
                self.assertEqual(ts_new.tseries[i][1], i)
            else:
                self.assertEqual(ts_new.tseries[i][1], 0)

        # combine with longer timeseries discard=True
        ts_long = self.ts_long.clone()

        ts_new = self.ts.combine(ts_long, discard=True)

        self.assertEqual(ts_new.tseries.shape[0], self.ts.tseries.shape[0])
        self.assertEqual(ts_new.tseries.shape[1], 2)

        # combine with longer timeseries discard=False pad=None
        self.assertRaises(
            ValueError, ts.combine, ts_long, discard=False, pad=None
        )

        # combine with longer timeseries discard=False pad=0
        ts_new = self.ts.combine(ts_long, discard=False, pad=0.0)

        for i in range(len(ts_new.tseries)):
            if i < len(self.ts.tseries):
                self.assertEqual(ts_new.tseries[i][0], i)
            else:
                self.assertEqual(ts_new.tseries[i][0], 0.0)

    def test_get_date_series_type(self):
        """Tests returning an appropriate date series type."""

        #   Day types
        self.assertEqual(self.ts.get_date_series_type(), TS_ORDINAL)

        self.ts.frequeny = "w"
        self.assertEqual(self.ts.get_date_series_type(), TS_ORDINAL)

        self.ts.frequeny = "m"
        self.assertEqual(self.ts.get_date_series_type(), TS_ORDINAL)

        self.ts.frequeny = "q"
        self.assertEqual(self.ts.get_date_series_type(), TS_ORDINAL)

        self.ts.frequeny = "y"
        self.assertEqual(self.ts.get_date_series_type(), TS_ORDINAL)

        #   Intraday types
        self.ts.frequency = "h"
        self.assertEqual(self.ts.get_date_series_type(), TS_TIMESTAMP)

        self.ts.frequency = "min"
        self.assertEqual(self.ts.get_date_series_type(), TS_TIMESTAMP)

        self.ts.frequency = "sec"
        self.assertEqual(self.ts.get_date_series_type(), TS_TIMESTAMP)

    def test_date_string_series(self):
        """Tests returning a list of dates in string format."""

        # ordinal default fmt
        str_series = self.ts.date_string_series()

        self.assertEqual(str_series[0], "2015-12-31")
        self.assertEqual(str_series[1], "2016-01-01")
        self.assertEqual(str_series[2], "2016-01-02")
        self.assertEqual(str_series[3], "2016-01-03")
        self.assertEqual(str_series[4], "2016-01-04")

        # timestamp default fmt
        ts = Timeseries(frequency="sec")

        ts.dseries = datetime(2016, 1, 1, 0, 0, 0).timestamp() + np.arange(10)
        ts.tseries = np.arange(10)
        ts.make_arrays()

        str_series = ts.date_string_series()

        self.assertEqual(str_series[0], "2016-01-01 00:00:00")
        self.assertEqual(str_series[1], "2016-01-01 00:00:01")
        self.assertEqual(str_series[2], "2016-01-01 00:00:02")
        self.assertEqual(str_series[3], "2016-01-01 00:00:03")
        self.assertEqual(str_series[4], "2016-01-01 00:00:04")

        # ordinal custom fmt
        str_series = self.ts.date_string_series("%Y-%b-%d")

        self.assertEqual(str_series[0], "2015-Dec-31")
        self.assertEqual(str_series[1], "2016-Jan-01")
        self.assertEqual(str_series[2], "2016-Jan-02")
        self.assertEqual(str_series[3], "2016-Jan-03")
        self.assertEqual(str_series[4], "2016-Jan-04")

    def test_timeseries_shape(self):
        """Tests returning the .shape of the tseries array."""

        self.assertTupleEqual(self.ts.shape(), self.ts.tseries.shape)

        self.assertTupleEqual(
            self.ts.combine(self.ts).shape(),
            (self.ts.tseries.shape[0], 2),
        )

    def test_sort_by_date(self):
        """Tests sorting the data by date."""

        # sort in reverse date order
        self.ts.sort_by_date(reverse=True)

        self.assertEqual(self.ts.dseries[0], datetime(2016, 1, 9).toordinal())
        self.assertEqual(self.ts.dseries[1], datetime(2016, 1, 8).toordinal())
        self.assertEqual(self.ts.dseries[2], datetime(2016, 1, 7).toordinal())
        self.assertEqual(self.ts.dseries[3], datetime(2016, 1, 6).toordinal())
        self.assertEqual(self.ts.dseries[4], datetime(2016, 1, 5).toordinal())
        self.assertEqual(self.ts.dseries[5], datetime(2016, 1, 4).toordinal())

        # sort in date order
        self.ts.sort_by_date(reverse=False)

        self.assertEqual(
            self.ts.dseries[0], datetime(2015, 12, 31).toordinal()
        )
        self.assertEqual(self.ts.dseries[1], datetime(2016, 1, 1).toordinal())
        self.assertEqual(self.ts.dseries[2], datetime(2016, 1, 2).toordinal())
        self.assertEqual(self.ts.dseries[3], datetime(2016, 1, 3).toordinal())
        self.assertEqual(self.ts.dseries[4], datetime(2016, 1, 4).toordinal())
        self.assertEqual(self.ts.dseries[5], datetime(2016, 1, 5).toordinal())

        # start with jumble of dates and sort in date order

        ts = self.ts.clone()

        ts.dateseries = [
            datetime(2016, 1, 9, 0, 0).toordinal(),
            datetime(2015, 12, 31, 0, 0).toordinal(),
            datetime(2016, 1, 8, 0, 0).toordinal(),
            datetime(2016, 1, 4, 0, 0).toordinal(),
            datetime(2016, 1, 7, 0, 0).toordinal(),
            datetime(2016, 1, 6, 0, 0).toordinal(),
            datetime(2016, 1, 1, 0, 0).toordinal(),
            datetime(2016, 1, 5, 0, 0).toordinal(),
            datetime(2016, 1, 3, 0, 0).toordinal(),
            datetime(2016, 1, 2, 0, 0).toordinal(),
        ]

        self.ts.sort_by_date(reverse=False, force=True)

        self.assertEqual(
            self.ts.dseries[0], datetime(2015, 12, 31).toordinal()
        )
        self.assertEqual(self.ts.dseries[1], datetime(2016, 1, 1).toordinal())
        self.assertEqual(self.ts.dseries[2], datetime(2016, 1, 2).toordinal())
        self.assertEqual(self.ts.dseries[3], datetime(2016, 1, 3).toordinal())
        self.assertEqual(self.ts.dseries[4], datetime(2016, 1, 4).toordinal())
        self.assertEqual(self.ts.dseries[5], datetime(2016, 1, 5).toordinal())

    def test_convert(self):
        """
        This function is a pass-through to the convert function.

        This version basically checks to see if the plumbing works. However,
        until the design decision is made on how to transition from intraday
        to monthly, etc., this cannot be considered complete.

        """

        ts = Timeseries()

        ts.dseries = datetime(2015, 12, 31).toordinal() + np.arange(1000)
        ts.tseries = np.arange(1000)

        ts_monthly = ts.convert(new_freq=FREQ_M, include_partial=True)

        self.assertEqual(ts_monthly.dseries[0], 735963)
        self.assertEqual(ts_monthly.dseries[1], 735994)
        self.assertEqual(ts_monthly.dseries[2], 736023)
        self.assertEqual(ts_monthly.dseries[3], 736054)
        self.assertEqual(ts_monthly.dseries[4], 736084)
        self.assertEqual(ts_monthly.dseries[5], 736115)
        self.assertEqual(ts_monthly.dseries[6], 736145)
        self.assertEqual(ts_monthly.dseries[7], 736176)
        self.assertEqual(ts_monthly.dseries[8], 736207)
        self.assertEqual(ts_monthly.dseries[9], 736237)

        self.assertEqual(ts_monthly.tseries[0], 0)
        self.assertEqual(ts_monthly.tseries[1], 31)
        self.assertEqual(ts_monthly.tseries[2], 60)
        self.assertEqual(ts_monthly.tseries[3], 91)
        self.assertEqual(ts_monthly.tseries[4], 121)
        self.assertEqual(ts_monthly.tseries[5], 152)
        self.assertEqual(ts_monthly.tseries[6], 182)
        self.assertEqual(ts_monthly.tseries[7], 213)
        self.assertEqual(ts_monthly.tseries[8], 244)
        self.assertEqual(ts_monthly.tseries[9], 274)

        self.assertEqual(ts_monthly.dseries[-1], 736962)
        self.assertEqual(ts_monthly.tseries[-1], 999)

        # bad frequency
        self.assertRaises(
            ValueError, ts.convert, new_freq="bad", include_partial=True
        )

        # if frequency is the same, do not do a second conversion
        ts = Timeseries()

        ts.tseries = np.arange(1000).reshape((-1, 1))
        ts.dseries = date.today().toordinal() + np.arange(1000)

        self.assertEqual(ts.frequency, "d")

        ts_m = ts.convert("m")

        self.assertEqual(ts_m.frequency, "m")
        self.assertDictEqual(ts_m.to_dict(), ts_m.convert("m").to_dict())

    def test_timeseries_reverse(self):
        """Tests reversing the order of both the dates and values."""

        ts = self.ts.clone()
        ts.reverse()

        # verify dateseries
        self.assertEqual(ts.dseries[0], datetime(2016, 1, 9).toordinal())
        self.assertEqual(ts.dseries[1], datetime(2016, 1, 8).toordinal())
        self.assertEqual(ts.dseries[2], datetime(2016, 1, 7).toordinal())
        self.assertEqual(ts.dseries[3], datetime(2016, 1, 6).toordinal())
        self.assertEqual(ts.dseries[4], datetime(2016, 1, 5).toordinal())
        self.assertEqual(ts.dseries[5], datetime(2016, 1, 4).toordinal())

        # verify values
        self.assertEqual(ts.tseries[0], 9)
        self.assertEqual(ts.tseries[1], 8)
        self.assertEqual(ts.tseries[2], 7)
        self.assertEqual(ts.tseries[3], 6)
        self.assertEqual(ts.tseries[4], 5)
        self.assertEqual(ts.tseries[5], 4)

        # verify with more than one column of data
        ts = self.ts.clone()

        ts = ts.combine(ts)
        ts.reverse()

        # verify values
        self.assertEqual(ts.tseries[0][0], 9)
        self.assertEqual(ts.tseries[1][0], 8)
        self.assertEqual(ts.tseries[2][0], 7)
        self.assertEqual(ts.tseries[3][0], 6)
        self.assertEqual(ts.tseries[4][0], 5)
        self.assertEqual(ts.tseries[5][0], 4)

        self.assertEqual(ts.tseries[0][1], 9)
        self.assertEqual(ts.tseries[1][1], 8)
        self.assertEqual(ts.tseries[2][1], 7)
        self.assertEqual(ts.tseries[3][1], 6)
        self.assertEqual(ts.tseries[4][1], 5)
        self.assertEqual(ts.tseries[5][1], 4)

    def test_timeseries_get_diffs(self):
        """Tests returning a timeseries that is the change in values."""

        ts = self.ts.get_diffs()

        self.assertListEqual(
            ts.tseries.tolist(),
            [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
        )

        self.assertEqual(len(ts.tseries), len(self.ts.tseries) - 1)

        self.assertTrue(np.array_equal(self.ts.dseries[1:], ts.dseries))

    def test_timeseries_get_pcdiffs(self):
        """Tests returning a timeseries that is % change in values."""

        ts = self.ts
        ts.tseries += 1
        ts1 = ts.get_pcdiffs()

        self.assertAlmostEqual(ts1.tseries[0], 100.0)
        self.assertAlmostEqual(ts1.tseries[1], 50.0)
        self.assertAlmostEqual(ts1.tseries[2], 33.33333333)
        self.assertAlmostEqual(ts1.tseries[3], 25.0)
        self.assertAlmostEqual(ts1.tseries[4], 20.0)
        self.assertAlmostEqual(ts1.tseries[5], 16.66666667)

        self.assertEqual(len(ts1.tseries), len(ts.tseries) - 1)

        self.assertTrue(np.array_equal(self.ts.dseries[1:], ts1.dseries))

    def test_timeseries_trunc(self):
        """Tests returning a timeseries that is a subset."""

        ts = self.ts.clone()
        ts.trunc(start=2, finish=None, new=False)
        self.assertTrue(np.array_equal(ts.tseries, self.ts.tseries[2:]))
        self.assertTrue(np.array_equal(ts.dseries, self.ts.dseries[2:]))

        ts = self.ts.clone()
        ts.trunc(start=None, finish=2, new=False)
        self.assertTrue(np.array_equal(ts.tseries, self.ts.tseries[:2]))
        self.assertTrue(np.array_equal(ts.dseries, self.ts.dseries[:2]))

        ts = self.ts.clone()
        ts.trunc(start=2, finish=4, new=False)
        self.assertTrue(np.array_equal(ts.tseries, self.ts.tseries[2:4]))
        self.assertTrue(np.array_equal(ts.dseries, self.ts.dseries[2:4]))

        ts = self.ts.clone()
        ts1 = ts.trunc(start=2, finish=4, new=True)
        self.assertTrue(np.array_equal(ts1.tseries, self.ts.tseries[2:4]))
        self.assertTrue(np.array_equal(ts1.dseries, self.ts.dseries[2:4]))

    def test_timeseries_truncdate(self):
        """
        Tests returning a timeseries that is a subset, but selected by
        date.
        """
        # set up separate timeseries with weekends skipped
        ts = Timeseries()
        ts.dseries = []
        ts.tseries = []
        start_date = datetime(2015, 12, 31)
        for i in range(40):
            date = start_date + timedelta(days=i)
            if date.weekday() not in [5, 6]:
                ts.dseries.append(date.toordinal())
                ts.tseries.append(i)

        ts.make_arrays()

        date1 = datetime(2016, 1, 7)  # existing date within date series
        date2 = datetime(2016, 1, 25)  # existing date within date series
        date3 = datetime(2016, 1, 16)  # date falling on a weekend

        # date as datetime
        ts1 = ts.clone()
        ts1.truncdate(start=date1, finish=None, new=False)

        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[5:]))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[5:]))

        # date as ordinal
        ts1 = ts.clone()
        ts1.truncdate(start=date1.toordinal(), finish=None, new=False)
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[5:]))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[5:]))

        # finish date
        ts1 = ts.clone()
        ts1.truncdate(start=None, finish=date2, new=False)
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[:18]))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[:18]))

        # finish date that is not in dseries
        ts1 = ts.clone()
        ts1.truncdate(start=None, finish=date3, new=False)
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[:12]))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[:12]))

        # start and finish date
        ts1 = ts.clone()
        ts1.truncdate(start=date1, finish=date2, new=False)
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[5:18]))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[5:18]))

        # start and finish date that is not in dseries
        ts1 = ts.clone()
        ts1.truncdate(start=date1, finish=date3, new=False)
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[5:12]))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[5:12]))

        # start and finish date as a list
        ts1 = ts.clone()
        ts1.truncdate([date1, date3], new=False)
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[5:12]))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[5:12]))

        # start and finish date as a tuple
        ts1 = ts.clone()
        ts1.truncdate((date1, date3), new=False)
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[5:12]))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[5:12]))

        # start and finish date as a tuple  new=True
        ts1 = ts.clone()
        ts2 = ts1.truncdate((date1, date3), new=True)
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries))
        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries))
        self.assertTrue(np.array_equal(ts2.tseries, ts.tseries[5:12]))
        self.assertTrue(np.array_equal(ts2.dseries, ts.dseries[5:12]))

    def test_timeseries_row_no(self):
        """Tests the ability to locate the correct row."""
        ts = Timeseries()
        ts.dseries = []
        ts.tseries = []

        start_date = datetime(2015, 12, 31)
        for i in range(40):
            date = start_date + timedelta(days=i)
            if date.weekday() not in [5, 6]:
                ts.dseries.append(date.toordinal())
                ts.tseries.append(i)

        ts.make_arrays()

        date1 = datetime(2016, 1, 7)  # existing date within date series
        date2 = datetime(2016, 1, 16)  # date falling on a weekend
        date3 = datetime(2015, 6, 16)  # date prior to start of date series
        date4 = datetime(2016, 3, 8)  # date after to end of date series

        # as datetime
        row_no = ts.row_no(rowdate=date1, closest=0, no_error=False)
        self.assertEqual(row_no, 5)

        # as ordinal
        row_no = ts.row_no(
            rowdate=date1.toordinal(), closest=0, no_error=False
        )
        self.assertEqual(row_no, 5)

        # as datetime but date not in series
        self.assertRaises(
            ValueError,
            ts.row_no,
            rowdate=date2,
            closest=0,
            no_error=False,
        )

        row_no = ts.row_no(rowdate=date2, closest=0, no_error=True)
        self.assertEqual(row_no, -1)

        # as datetime but date not in series, look for earlier date
        row_no = ts.row_no(rowdate=date2, closest=-1, no_error=False)
        self.assertEqual(row_no, 11)

        # as datetime but date not in series, look for later date
        row_no = ts.row_no(rowdate=date2, closest=1, no_error=False)
        self.assertEqual(row_no, 12)

        # as datetime but date not in series, look for earlier date
        self.assertRaises(
            ValueError,
            ts.row_no,
            rowdate=date3,
            closest=-1,
            no_error=False,
        )

        # as datetime but date not in series, look for later date
        self.assertRaises(
            ValueError,
            ts.row_no,
            rowdate=date4,
            closest=1,
            no_error=False,
        )

        # now change series direction
        ts.reverse()

        # as datetime
        row_no = ts.row_no(rowdate=date1, closest=0, no_error=False)
        self.assertEqual(row_no, 22)

        # as ordinal
        row_no = ts.row_no(
            rowdate=date1.toordinal(), closest=0, no_error=False
        )
        self.assertEqual(row_no, 22)

        # as datetime but date not in series
        self.assertRaises(
            ValueError,
            ts.row_no,
            rowdate=date2,
            closest=0,
            no_error=False,
        )

        row_no = ts.row_no(rowdate=date2, closest=0, no_error=True)
        self.assertEqual(row_no, -1)

        # as datetime but date not in series, look for earlier date
        row_no = ts.row_no(rowdate=date2, closest=-1, no_error=False)
        self.assertEqual(row_no, 16)

        # as datetime but date not in series, look for later date
        row_no = ts.row_no(rowdate=date2, closest=1, no_error=False)
        self.assertEqual(row_no, 15)

        # as datetime but date not in series, look for earlier date
        self.assertRaises(
            ValueError,
            ts.row_no,
            rowdate=date3,
            closest=-1,
            no_error=False,
        )

        # as datetime but date not in series, look for later date
        self.assertRaises(
            ValueError,
            ts.row_no,
            rowdate=date4,
            closest=1,
            no_error=False,
        )

    def test_timeseries_datetime_series(self):
        """Tests returning a date series converted to date/datetime objects."""

        ord_list = datetime(2016, 1, 1).toordinal() + np.arange(20)
        tstamp_list = datetime(2016, 1, 1).timestamp() + np.arange(20)

        ts = Timeseries()
        ts.dseries = ord_list
        ts.tseries = np.arange(20)  # gilding the lily

        dt_list = [date(2016, 1, 1) + timedelta(days=i) for i in range(20)]

        self.assertListEqual(ts.datetime_series(), dt_list)

        ts.frequency = FREQ_SEC
        ts.dseries = tstamp_list
        ts.tseries = np.arange(20)

        dt_list = [
            datetime(2016, 1, 1) + timedelta(seconds=i) for i in range(20)
        ]

        self.assertListEqual(ts.datetime_series(), dt_list)

    def test_timeseries_fmt_date(self):
        """Tests formatting str dates based on date types."""
        # ordinal date default format
        ts = Timeseries()
        str_date = ts.fmt_date(
            datetime(2016, 3, 1).toordinal(), dt_type=TS_ORDINAL
        )

        self.assertEqual(str_date, "2016-03-01")

        # ordinal date custom format
        str_date = ts.fmt_date(
            datetime(2016, 3, 1).toordinal(),
            dt_type=TS_ORDINAL,
            dt_fmt="%g %b %d",
        )

        self.assertEqual(str_date, "16 Mar 01")

        # timestamp date default format
        ts = Timeseries(frequency=FREQ_SEC)
        str_date = ts.fmt_date(
            datetime(2016, 3, 1).timestamp(), dt_type=TS_TIMESTAMP
        )

        self.assertEqual(str_date, "2016-03-01 00:00:00")

        # timestamp date custom format
        str_date = ts.fmt_date(
            datetime(2016, 3, 1, 10, 5, 23, 45).timestamp(),
            dt_type=TS_TIMESTAMP,
            dt_fmt="%F at %H:%M and %S seconds",
        )

        self.assertEqual(str_date, "2016-03-01 at 10:05 and 23 seconds")

        # invalid date type
        self.assertRaises(
            ValueError,
            ts.fmt_date,
            datetime(2020, 1, 29),
            dt_type=None,
            dt_fmt="%F",
        )

    def test_timeseries__repr__(self):
        """
        <Timeseries>
        key: Test Key
        columns: []
        frequency: d
        daterange: ('2016-01-09', '2015-12-31')
        end-of-period: True
        shape: (10,)
        """
        str_ts = str(self.ts).split("\n")
        self.assertEqual("<Timeseries>", str_ts[0])
        self.assertEqual("key: Test Key", str_ts[1])
        self.assertEqual("columns: ['F1']", str_ts[2])
        self.assertEqual("frequency: d", str_ts[3])
        self.assertEqual("daterange: ('2015-12-31', '2016-01-09')", str_ts[4])
        self.assertEqual("end-of-period: True", str_ts[5])
        self.assertEqual("shape: (10,)", str_ts[6])

        # test blank Timeseries
        ts = Timeseries()
        str_ts = str(ts).split("\n")
        self.assertEqual("<Timeseries>", str_ts[0])
        self.assertEqual("key: ", str_ts[1])
        self.assertEqual("columns: None", str_ts[2])
        self.assertEqual("frequency: d", str_ts[3])
        self.assertEqual("daterange: (None, None)", str_ts[4])
        self.assertEqual("end-of-period: True", str_ts[5])
        self.assertEqual("shape: None", str_ts[6])

    def test_timeseries_set_zeros(self):
        """This function tests whether the timeseries can be set to zeros."""
        ts = self.ts.clone()
        shape = ts.shape()

        ts.set_zeros()

        self.assertTrue(np.array_equal(ts.tseries, np.zeros(shape)))

        ts1 = self.ts.clone().set_zeros(new=True)
        self.assertTrue(np.array_equal(ts1.tseries, np.zeros(shape)))

    def test_timeseries_set_ones(self):
        """This function tests whether the timeseries can be set to ones."""
        ts = self.ts.clone()
        shape = ts.shape()

        ts.set_ones()

        self.assertTrue(np.array_equal(ts.tseries, np.ones(shape)))

        ts1 = self.ts.clone().set_ones(new=True)
        self.assertTrue(np.array_equal(ts1.tseries, np.ones(shape)))

    def test_timeseries_header(self):
        """Tests returning the non-timeseries data."""

        header_dict = self.ts.header()

        self.assertDictEqual(
            header_dict,
            {
                "frequency": "d",
                "key": "Test Key",
                "columns": ["F1"],
                "end_of_period": True,
            },
        )

    def test_timeseries_daterange(self):
        """Tests returning the starting and ending dates in various formats."""
        # ordinal daterange as ordinals,
        self.assertTupleEqual(
            self.ts.daterange(),
            (
                datetime(2015, 12, 31).toordinal(),
                datetime(2016, 1, 9).toordinal(),
            ),
        )

        # ordinal daterange as string
        self.assertTupleEqual(
            self.ts.daterange("str"), ("2015-12-31", "2016-01-09")
        )

        # ordinal daterange as datetimes
        self.assertTupleEqual(
            self.ts.daterange("datetime"),
            (date(2015, 12, 31), date(2016, 1, 9)),
        )

        # timestamp
        tstamp_list = datetime(2016, 1, 1).timestamp() + np.arange(20)

        ts = Timeseries()
        ts.frequency = FREQ_SEC
        ts.dseries = tstamp_list
        ts.tseries = np.arange(20)

        # timestamp daterange as timestamps
        self.assertTupleEqual(
            ts.daterange(),
            (
                datetime(2016, 1, 1).timestamp(),
                datetime(2016, 1, 1, 0, 0, 19).timestamp(),
            ),
        )

        # timestamp daterange as string
        self.assertTupleEqual(
            ts.daterange("str"),
            ("2016-01-01 00:00:00", "2016-01-01 00:00:19"),
        )

        # timestamp daterange as datetimes
        self.assertTupleEqual(
            ts.daterange("datetime"),
            (
                datetime(2016, 1, 1, 0, 0, 0),
                datetime(2016, 1, 1, 0, 0, 19),
            ),
        )

        # test blank Timeseries
        ts = Timeseries()
        self.assertTupleEqual(ts.daterange(), (None, None))

        # test invalid format flag
        self.assertRaises(ValueError, self.ts.daterange, fmt="wrong")

    def test_timeseries_years(self):
        """Tests returning the ending values by years in a dict."""

        ts = Timeseries()
        ts.dseries = datetime(2015, 12, 31).toordinal() + np.arange(1000)
        ts.tseries = np.arange(1000)

        self.assertDictEqual(
            ts.years(),
            {
                2015: 0,
                2016: 366,
                2017: 731,
                2018: 999,
            },
        )

    def test_timeseries_months(self):
        """Tests returning the ending values by months in a dict."""
        ts = Timeseries()
        ts.dseries = datetime(2015, 12, 31).toordinal() + np.arange(1000)
        ts.tseries = np.arange(1000)

        self.assertDictEqual(
            ts.months(),
            {
                "2015-12": 0,
                "2016-01": 31,
                "2016-02": 60,
                "2016-03": 91,
                "2016-04": 121,
                "2016-05": 152,
                "2016-06": 182,
                "2016-07": 213,
                "2016-08": 244,
                "2016-09": 274,
                "2016-10": 305,
                "2016-11": 335,
                "2016-12": 366,
                "2017-01": 397,
                "2017-02": 425,
                "2017-03": 456,
                "2017-04": 486,
                "2017-05": 517,
                "2017-06": 547,
                "2017-07": 578,
                "2017-08": 609,
                "2017-09": 639,
                "2017-10": 670,
                "2017-11": 700,
                "2017-12": 731,
                "2018-01": 762,
                "2018-02": 790,
                "2018-03": 821,
                "2018-04": 851,
                "2018-05": 882,
                "2018-06": 912,
                "2018-07": 943,
                "2018-08": 974,
                "2018-09": 999,
            },
        )

    def test_timeseries_closest_date(self):
        """Tests returning the closest date in the series to the input date."""

        ts = Timeseries()
        ts.dseries = []
        ts.tseries = []

        start_date = datetime(2015, 12, 31)
        for i in range(40):
            date = start_date + timedelta(days=i)
            if date.weekday() not in [5, 6]:
                ts.dseries.append(date.toordinal())
                ts.tseries.append(i)

        ts.make_arrays()

        date1 = datetime(2016, 1, 7)  # existing date within date series
        date2 = datetime(2016, 1, 16)  # date falling on a weekend
        date3 = datetime(2015, 6, 16)  # date prior to start of date series
        date4 = datetime(2016, 3, 8)  # date after to end of date series

        # as datetime and in the series
        test_date = ts.closest_date(rowdate=date1, closest=1)
        self.assertEqual(test_date, date1.toordinal())

        # as ordinal and in the series
        test_date = ts.closest_date(rowdate=date1, closest=1)
        self.assertEqual(test_date, date1.toordinal())

        # as datetime but date not in series
        test_date = ts.closest_date(rowdate=date2, closest=1)
        self.assertEqual(test_date, datetime(2016, 1, 18).toordinal())

        test_date = ts.closest_date(rowdate=date2, closest=-1)
        self.assertEqual(test_date, datetime(2016, 1, 15).toordinal())

        # as datetime but date not in series, look for earlier date
        self.assertRaises(
            ValueError, ts.closest_date, rowdate=date3, closest=-1
        )

        # as datetime but date not in series, look for later date
        self.assertRaises(
            ValueError, ts.closest_date, rowdate=date4, closest=1
        )

    def test_timeseries_get_duped_dates(self):
        """Test the dupes works properly."""
        ts = self.ts.clone()

        ts.dseries[3] = ts.dseries[4]

        ts = Timeseries(frequency="sec")

        ts.dseries = datetime(2015, 12, 31).timestamp() + np.arange(10)
        ts.tseries = np.arange(10)
        ts.make_arrays()

        ts.dseries[3] = ts.dseries[4]

    def test_items(self):
        """This function returns a combined date and values list."""

        items = [
            (date(2015, 12, 31), 0.0),
            (date(2016, 1, 1), 1.0),
            (date(2016, 1, 2), 2.0),
            (date(2016, 1, 3), 3.0),
            (date(2016, 1, 4), 4.0),
            (date(2016, 1, 5), 5.0),
            (date(2016, 1, 6), 6.0),
            (date(2016, 1, 7), 7.0),
            (date(2016, 1, 8), 8.0),
            (date(2016, 1, 9), 9.0),
        ]

        self.assertListEqual(self.ts.items(), items)

        self.assertListEqual(
            self.ts.items("str"),
            [
                (date, values)
                for date, values in zip(
                    self.ts.date_string_series(), self.ts.tseries
                )
            ],
        )

    def test_get_point(self):
        """
        This function tests getting a point object from a timeseries row.
        """

        point = self.ts.get_point(row_no=0)

        self.assertEqual(point.row_no, 0)
        self.assertEqual(point.date, self.ts.dseries[0])
        self.assertEqual(point.values, self.ts.tseries[0])

        self.ts.tseries = self.ts.tseries.reshape((-1, 1))

        point = self.ts.get_point(row_no=0)
        self.assertListEqual(
            point.values.tolist(), self.ts.tseries[0].tolist()
        )

        # by rowdate
        point = self.ts.get_point(rowdate=self.ts.start_date())
        self.assertEqual(point.row_no, 0)
        self.assertEqual(point.date, self.ts.dseries[0])
        self.assertEqual(point.values, self.ts.tseries[0])

        # no params
        self.assertRaises(ValueError, self.ts.get_point)


if __name__ == "__main__":
    unittest.main()
