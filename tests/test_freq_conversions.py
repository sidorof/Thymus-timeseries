"""
This module tests the conversions from one frequency to another.

"""

from datetime import datetime, timedelta
import numpy as np

import unittest

from thymus.timeseries import Timeseries
from thymus.constants import FREQ_D, FREQ_W, FREQ_M, FREQ_Q, FREQ_Y
from thymus.constants import FREQ_H, FREQ_MIN

from thymus.freq_conversions import convert


class TestFreqConversions(unittest.TestCase):
    """
    This class tests conversions of timeseries.
    """

    def setUp(self):
        # sample timeseries
        self.ts_ord = Timeseries()
        start_date = datetime(2015, 12, 31)

        # sloppily ends slightly more than two years
        end_date = datetime(2018, 1, 15)

        # set up two years of data with weekends skipped
        date = start_date
        self.ts_ord.dseries = []
        while date <= end_date:
            if date.weekday() not in [5, 6]:
                self.ts_ord.dseries.append(date.toordinal())
            date += timedelta(days=1)

        self.ts_ord.tseries = np.arange(len(self.ts_ord.dseries))
        self.ts_ord.make_arrays()

        # timestamp based timeseries
        self.ts_seconds = Timeseries(frequency="sec")
        start_date = datetime(2016, 1, 1, 0, 0)
        end_date = datetime(2016, 1, 4, 0, 0)

        length = (end_date - start_date).total_seconds()

        self.ts_seconds.dseries = start_date.timestamp() + np.arange(length)
        self.ts_seconds.tseries = np.arange(length)
        self.ts_seconds.make_arrays()

    def test_convweekly_period_start(self):
        """Test timeseries conversion to weekly with start-of-period data."""
        ts = self.ts_ord.clone()
        ts.end_of_period = False

        # conv_weekly with defaults
        ts1 = convert(ts, new_freq=FREQ_W)

        self.assertEqual(ts1.frequency, FREQ_W)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 4).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 11).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 1, 18).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 1, 25).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 2, 1).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 2, 8).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 8).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_weekly with include_partial=True
        ts1 = convert(ts, new_freq=FREQ_W, include_partial=True)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 4).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 11).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 1, 18).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 1, 25).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 2, 1).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 2, 8).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 8).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        ts1 = convert(ts, new_freq=FREQ_W, include_partial=False)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 4).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 11).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 1, 18).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 1, 25).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 2, 1).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 2, 8).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        ts1 = convert(ts, new_freq=FREQ_W, weekday=2)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 7).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 14).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 1, 21).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 1, 28).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 2, 4).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 2, 11).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 11).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # test lower frequency data
        self.assertRaises(
            ValueError,
            convert,
            convert(self.ts_ord, new_freq=FREQ_Y),
            new_freq=FREQ_W,
        )

    def test_convweekly_period_end(self):
        """
        Test timeseries conversion to weekly with end-of-period data.
        """
        ts = self.ts_ord.clone()

        # conv_weekly with defaults
        ts1 = convert(ts, new_freq=FREQ_W)

        self.assertEqual(ts1.frequency, FREQ_W)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 8).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 1, 15).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 1, 22).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 1, 29).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 2, 5).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 12).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_weekly with include_partial=True
        ts1 = convert(ts, new_freq=FREQ_W, include_partial=True)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 8).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 1, 15).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 1, 22).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 1, 29).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 2, 5).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 12).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_weekly with include_partial=False
        ts1 = convert(ts, new_freq=FREQ_W, include_partial=False)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 8).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 1, 15).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 1, 22).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 1, 29).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 2, 5).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 12).toordinal())

        # conv_weekly with weekday=2
        ts1 = convert(ts, new_freq=FREQ_W, weekday=2)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 6).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 13).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 1, 20).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 1, 27).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 2, 3).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 2, 10).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 10).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # test lower frequency data
        self.assertRaises(
            ValueError,
            convert,
            convert(self.ts_ord, new_freq=FREQ_Y),
            new_freq=FREQ_W,
        )

    def test_convmonthly_period_start(self):
        """
        This function tests converting timeseries to monthly data that have
        starting period data.

        """

        # daily_monthly(ts, new_freq):
        ts = self.ts_ord.clone()
        ts.end_of_period = False

        # daily_monthly with defaults
        ts1 = convert(ts, new_freq=FREQ_M)

        self.assertEqual(ts1.frequency, FREQ_M)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 2, 1).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 3, 1).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 4, 1).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 5, 2).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 6, 1).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2016, 7, 1).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_monthly with include_partial=True
        ts1 = convert(ts, new_freq=FREQ_M, include_partial=True)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 2, 1).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 3, 1).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 4, 1).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 5, 2).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 6, 1).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2016, 7, 1).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_monthly with include_partial=False
        ts1 = convert(ts, new_freq=FREQ_M, include_partial=False)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 2, 1).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 3, 1).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 4, 1).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 5, 2).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 6, 1).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2016, 7, 1).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 1).toordinal())

        # test lower frequency data
        self.assertRaises(
            ValueError,
            convert,
            convert(self.ts_ord, new_freq="y"),
            new_freq=FREQ_M,
        )

        # timestamp conversion goes here

    def test_convmonthly_period_end(self):
        """
        This function tests converting timeseries to monthly data that have
        ending period data.

        """
        ts = self.ts_ord.clone()

        # daily_monthly with defaults
        ts1 = convert(ts, new_freq=FREQ_M)

        self.assertEqual(ts1.frequency, FREQ_M)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 29).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 2, 29).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 4, 29).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 5, 31).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2016, 6, 30).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2017, 12, 29).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_monthly with include_partial=True
        ts1 = convert(ts, new_freq=FREQ_M, include_partial=True)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 29).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 2, 29).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 4, 29).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 5, 31).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2016, 6, 30).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2017, 12, 29).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_monthly with include_partial=False
        ts1 = convert(ts, new_freq=FREQ_M, include_partial=False)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 1, 29).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 2, 29).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 4, 29).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2016, 5, 31).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2016, 6, 30).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-1], datetime(2017, 12, 29).toordinal())

        # test lower frequency data
        self.assertRaises(
            ValueError,
            convert,
            convert(self.ts_ord, new_freq=FREQ_Y),
            new_freq=FREQ_M,
        )

        # timestamp conversion goes here

    def test_convquarterly_period_start(self):
        """
        This function tests converting timeseries to quarterly data that have
        starting period data.

        """

        # conv_quarterly(ts, new_freq):
        ts = self.ts_ord.clone()
        ts.end_of_period = False

        # conv_quarterly with defaults
        ts1 = convert(ts, new_freq=FREQ_Q)

        self.assertEqual(ts1.frequency, FREQ_Q)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 4, 1).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 7, 1).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 10, 3).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2017, 1, 2).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2017, 4, 3).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2017, 7, 3).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_quarterly with include_partial=True
        ts1 = convert(ts, new_freq=FREQ_Q, include_partial=True)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 4, 1).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 7, 1).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 10, 3).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2017, 1, 2).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2017, 4, 3).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2017, 7, 3).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2018, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_quarterly with include_partial=False
        ts1 = convert(ts, new_freq=FREQ_Q, include_partial=False)

        self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 4, 1).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 7, 1).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 10, 3).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2017, 1, 2).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2017, 4, 3).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2017, 7, 3).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 1).toordinal())

        # unresolved design decision
        # with monthly data
        # ts1 = convert(
        #    convert(ts, new_freq=FREQ_M, include_partial=False),
        #    new_freq=FREQ_Q,
        #    include_partial=False)

        # self.assertEqual(ts1.dseries[0], datetime(2016, 1, 1).toordinal())
        # self.assertEqual(ts1.dseries[1], datetime(2016, 4, 1).toordinal())
        # self.assertEqual(ts1.dseries[2], datetime(2016, 7, 1).toordinal())
        # self.assertEqual(ts1.dseries[3], datetime(2016, 10, 3).toordinal())
        # self.assertEqual(ts1.dseries[4], datetime(2017, 1, 2).toordinal())
        # self.assertEqual(ts1.dseries[5], datetime(2017, 4, 3).toordinal())
        # self.assertEqual(ts1.dseries[6], datetime(2017, 7, 3).toordinal())

        # ending values
        # self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 1).toordinal())

        # test lower frequency data
        self.assertRaises(
            ValueError,
            convert,
            convert(self.ts_ord, new_freq=FREQ_Y),
            new_freq=FREQ_Q,
        )

        # timestamp conversion goes here

    def test_convquarterly_period_end(self):
        """
        This function tests converting timeseries to quarterly data that have
        ending period data.

        """

        ts = self.ts_ord.clone()

        ts1 = convert(ts, new_freq=FREQ_Q)

        self.assertEqual(ts1.frequency, FREQ_Q)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 6, 30).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 9, 30).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2017, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2017, 6, 30).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2017, 12, 29).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_quarterly with include_partial=True
        ts1 = convert(ts, new_freq=FREQ_Q, include_partial=True)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 6, 30).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 9, 30).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2017, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2017, 6, 30).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-2], datetime(2017, 12, 29).toordinal())
        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_quarterly with include_partial=False
        ts1 = convert(ts, new_freq=FREQ_Q, include_partial=False)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2016, 6, 30).toordinal())
        self.assertEqual(ts1.dseries[3], datetime(2016, 9, 30).toordinal())
        self.assertEqual(ts1.dseries[4], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[5], datetime(2017, 3, 31).toordinal())
        self.assertEqual(ts1.dseries[6], datetime(2017, 6, 30).toordinal())

        # ending values
        self.assertEqual(ts1.dseries[-1], datetime(2017, 12, 29).toordinal())

        # resolve design decision
        # ts1 = convert(
        #    convert(ts, new_freq=FREQ_M, include_partial=False),
        #    new_freq=FREQ_Q,
        #    include_partial=False)

        # self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        # self.assertEqual(ts1.dseries[1], datetime(2016, 3, 31).toordinal())
        # self.assertEqual(ts1.dseries[2], datetime(2016, 6, 30).toordinal())
        # self.assertEqual(ts1.dseries[3], datetime(2016, 9, 30).toordinal())
        # self.assertEqual(ts1.dseries[4], datetime(2016, 12, 30).toordinal())
        # self.assertEqual(ts1.dseries[5], datetime(2017, 3, 31).toordinal())
        # self.assertEqual(ts1.dseries[6], datetime(2017, 6, 30).toordinal())

        # ending values
        # self.assertEqual(ts1.dseries[-1], datetime(2017, 12, 29).toordinal())

        # test lower frequency data
        # test lower frequency data
        self.assertRaises(
            ValueError,
            convert,
            convert(self.ts_ord, new_freq=FREQ_Y),
            new_freq=FREQ_Q,
        )

        # timestamp conversion goes here

    def test_convyearly_period_start(self):
        """
        This function tests converting timeseries to yearly data that have
        starting period data.

        """

        ts = self.ts_ord.clone()

        # conv_yearly with defaults
        ts1 = convert(ts, new_freq=FREQ_Y)

        self.assertEqual(ts1.frequency, FREQ_Y)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2017, 12, 29).toordinal())

        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_yearly with include_partial=True
        ts1 = convert(ts, new_freq=FREQ_Y, include_partial=True)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2017, 12, 29).toordinal())

        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_yearly with include_partial=False
        ts1 = convert(ts, new_freq=FREQ_Y, include_partial=False)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2017, 12, 29).toordinal())

        # resolve design decision
        # with monthly data
        # ts1 = convert(
        #    convert(ts, new_freq=FREQ_M, include_partial=False),
        #    new_freq=FREQ_Y,
        #    include_partial=False)

        # self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        # self.assertEqual(ts1.dseries[1], datetime(2016, 12, 30).toordinal())
        # self.assertEqual(ts1.dseries[2], datetime(2017, 12, 29).toordinal())

        # timestamp conversion goes here

    def test_convyearly_period_end(self):
        """
        This function tests converting timeseries to yearly data that have
        ending period data.

        """

        ts = self.ts_ord.clone()

        # conv_yearly with defaults
        ts1 = convert(ts, new_freq=FREQ_Y)

        self.assertEqual(ts1.frequency, FREQ_Y)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2017, 12, 29).toordinal())

        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_yearly with include_partial=True
        ts1 = convert(ts, new_freq=FREQ_Y, include_partial=True)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2017, 12, 29).toordinal())

        self.assertEqual(ts1.dseries[-1], datetime(2018, 1, 15).toordinal())

        # conv_yearly with include_partial=False
        ts1 = convert(ts, new_freq=FREQ_Y, include_partial=False)

        self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        self.assertEqual(ts1.dseries[1], datetime(2016, 12, 30).toordinal())
        self.assertEqual(ts1.dseries[2], datetime(2017, 12, 29).toordinal())

        # resolve design decision
        # with monthly data
        # ts1 = convert(
        #    convert(ts, new_freq=FREQ_M, include_partial=False),
        #    new_freq=FREQ_Y,
        #    include_partial=False)

        # self.assertEqual(ts1.dseries[0], datetime(2015, 12, 31).toordinal())
        # self.assertEqual(ts1.dseries[1], datetime(2016, 12, 30).toordinal())
        # self.assertEqual(ts1.dseries[2], datetime(2017, 12, 29).toordinal())

        # timestamp conversion goes here

    def test_convminutes_period_start(self):
        """
        This function tests converting timeseries to minute data that have
        starting period data.

        """

        ts = self.ts_seconds.clone()
        ts.end_of_period = False

        ts1 = convert(ts, new_freq=FREQ_MIN)

        self.assertEqual(
            ts1.dseries[0], datetime(2016, 1, 1, 0, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[1], datetime(2016, 1, 1, 0, 1, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[2], datetime(2016, 1, 1, 0, 2, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[3], datetime(2016, 1, 1, 0, 3, 0).timestamp()
        )

    @unittest.skip
    def test_convminutes_period_end(self):
        """
        This function tests converting timeseries to minute data that have
        ending period data.

        Needs design decision.
        """

        ts = self.ts_seconds.clone()

        ts1 = convert(ts, new_freq=FREQ_MIN)

        self.assertEqual(
            ts1.dseries[0], datetime(2016, 1, 1, 0, 0, 59).timestamp()
        )
        self.assertEqual(
            ts1.dseries[1], datetime(2016, 1, 1, 0, 1, 59).timestamp()
        )
        self.assertEqual(
            ts1.dseries[2], datetime(2016, 1, 1, 0, 2, 59).timestamp()
        )
        self.assertEqual(
            ts1.dseries[3], datetime(2016, 1, 1, 0, 3, 59).timestamp()
        )
        self.assertEqual(
            ts1.dseries[4], datetime(2016, 1, 1, 0, 4, 59).timestamp()
        )
        self.assertEqual(
            ts1.dseries[5], datetime(2016, 1, 1, 0, 5, 59).timestamp()
        )

    def test_convhours_period_start(self):
        """
        This function tests conversion to hours.

        Currently there is a problem with this. At the moment it a design
        decision needs to be made on how to handle end-of-period conversions.

        """
        ts = self.ts_seconds.clone()
        ts.end_of_period = False
        ts1 = convert(ts, new_freq=FREQ_H)

        self.assertEqual(
            ts1.dseries[0], datetime(2016, 1, 1, 0, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[1], datetime(2016, 1, 1, 1, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[2], datetime(2016, 1, 1, 2, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[3], datetime(2016, 1, 1, 3, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[4], datetime(2016, 1, 1, 4, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[5], datetime(2016, 1, 1, 5, 0, 0).timestamp()
        )

    @unittest.skip
    def test_convhours_period_end(self):
        """
        This function tests conversion to hours.

        Currently there is a problem with this. At the moment a design
        decision needs to be made on how to handle end-of-period conversions.

        """

        ts = self.ts_seconds.clone()
        ts.end_of_period = False
        ts1 = convert(ts, new_freq=FREQ_H)

        ts = self.ts_seconds.clone()
        ts.end_of_period = True
        ts1 = convert(ts, new_freq=FREQ_H)

        self.assertEqual(
            ts1.dseries[0], datetime(2016, 1, 1, 0, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[1], datetime(2016, 1, 1, 1, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[2], datetime(2016, 1, 1, 2, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[3], datetime(2016, 1, 1, 3, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[4], datetime(2016, 1, 1, 4, 0, 0).timestamp()
        )
        self.assertEqual(
            ts1.dseries[5], datetime(2016, 1, 1, 5, 0, 0).timestamp()
        )

    @unittest.skip
    def test_conv_days(self):
        """
        This function converts timestamp data to a daily frequency with
        ordinal dates.

        Currently, there is a problem with this.
        """

        ts = self.ts_seconds.clone()

        ts.end_of_period = False

        ts1 = convert(ts, new_freq=FREQ_D)

        self.assertEqual(
            ts1.dseries[0], datetime(2016, 1, 1, 0, 0, 0).toordinal()
        )
        self.assertEqual(
            ts1.dseries[1], datetime(2016, 1, 2, 0, 0, 0).toordinal()
        )
        self.assertEqual(
            ts1.dseries[2], datetime(2016, 1, 3, 0, 0, 0).toordinal()
        )
        self.assertEqual(
            ts1.dseries[3], datetime(2016, 1, 4, 0, 0, 0).toordinal()
        )

        ts = self.ts_seconds.clone()
        ts.end_of_period = True

        ts1 = convert(ts, new_freq=FREQ_D)

        self.assertEqual(
            ts1.dseries[0], datetime(2016, 1, 1, 0, 0, 0).toordinal()
        )
        self.assertEqual(
            ts1.dseries[1], datetime(2016, 1, 2, 0, 0, 0).toordinal()
        )
        self.assertEqual(
            ts1.dseries[2], datetime(2016, 1, 3, 0, 0, 0).toordinal()
        )
        self.assertEqual(
            ts1.dseries[3], datetime(2016, 1, 4, 0, 0, 0).toordinal()
        )


if __name__ == "__main__":
    unittest.main()
