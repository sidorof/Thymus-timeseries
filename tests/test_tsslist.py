"""
This module tests the TssList class
"""

from datetime import datetime
import numpy as np

import unittest

from thymus.timeseries import Timeseries
from thymus.tsslist import TssList


class TestTssList(unittest.TestCase):
    """ This class tests the class TssList. """
    def setUp(self):

        # three timeseries
        self.ts = Timeseries()
        self.ts.key = 'Test Key'
        self.ts.columns = ['F1']

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

        self.tss = TssList([self.ts, self.ts_long, self.ts_short])

    def test_class_init_(self):
        """Test class initialization."""

        self.assertEqual(len(self.tss), 3)

        tmp_ts0 = Timeseries()
        tmp_ts1 = Timeseries()
        tmp_ts2 = Timeseries()

        tss = TssList()

        self.assertEqual(len(tss), 0)

        tss.append(Timeseries())
        tss.append(Timeseries())
        tss.append(Timeseries())

        self.assertEqual(len(tss), 3)

    def test_tsslist_min_date(self):
        """Tests min date """
        self.assertEqual(self.tss.min_date(), self.ts.start_date('datetime'))

        tmp_ts0 = Timeseries()

        tmp_ts0.dseries = datetime(2014, 12, 31).toordinal() + np.arange(10)
        tmp_ts0.tseries = np.arange(10)
        tmp_ts0.make_arrays()

        self.tss.append(tmp_ts0)

        self.assertEqual(self.tss.min_date(), datetime(2014, 12, 31))

    def test_tsslist_max_date(self):
        """Tests max date """

        self.assertEqual(self.tss.max_date(), datetime(2016, 1, 19))

        tmp_ts0 = Timeseries()

        tmp_ts0.dseries = datetime(2018, 12, 31).toordinal() - np.arange(10)
        tmp_ts0.tseries = np.arange(10)
        tmp_ts0.make_arrays()

        self.tss.append(tmp_ts0)

        self.assertEqual(self.tss.max_date(), datetime(2018, 12, 31))

    def test_tsslist_combine(self):
        """
        A batch of tests combining columns to one timeseries.

        Tests check to see whether the parameters are passed down properly to
        each timeseries.
        """

        # combine(self, discard=True, pad=None)
        ts_new = self.tss.combine(discard=True, pad=None)

        # shape corresponds to the shortest length
        self.assertEqual(
            ts_new.tseries.shape[0],
            self.ts_short.tseries.shape[0])

        self.assertEqual(ts_new.tseries.shape[1], 3)

        # combine(self, discard=False, pad=0)
        ts_new = self.tss.combine(discard=False, pad=0)

        # shape corresponds to the longest length
        self.assertEqual(
            ts_new.tseries.shape[0],
            self.ts_long.tseries.shape[0])

        self.assertEqual(ts_new.tseries.shape[1], 3)

    def test_tsslist_get_values(self):
        """ Tests the ability to locate the correct row of data. """

        date1 = datetime(2016, 1, 4)    # existing date within date series
        date2 = datetime(2016, 1, 16)   # date falling on a weekend

        # get data from existing date
        self.assertTupleEqual(self.tss.get_values(date=date1), (4.0, 4.0, 4.0))

        # attempt to get data from date not present, with notify
        self.assertRaises(ValueError, self.tss.get_values, date2, notify=True)

        # attempt to get data from date not present, no notify
        self.assertTupleEqual(
            self.tss.get_values(date=date2), (None, 16.0, None))

    def test_clone(self):
        """Verifies that a copy is made."""
        tss = self.tss.clone()

        # is it a separate object
        for i in range(len(tss)):
            ts_orig = self.tss[i]
            ts_new = tss[i]
            #self.assertEqual(ts_new, ts_orig)
            self.assertNotEqual(ts_new, ts_orig)

        # do the characteristics match up?
        self.assertEqual(len(tss), 3)

        ts_orig = self.tss[0]
        ts_copy = tss[0]

        self.assertEqual(ts_copy.key, ts_orig.key)
        self.assertEqual(ts_copy.frequency, ts_orig.frequency)
        self.assertTrue(np.array_equal(ts_copy.tseries, ts_orig.tseries))
        self.assertTrue(np.array_equal(ts_copy.dseries, ts_orig.dseries))
        self.assertListEqual(ts_copy.columns, ts_orig.columns)
        self.assertEqual(ts_copy.end_of_period, ts_orig.end_of_period)

        ts_orig = self.tss[1]
        ts_copy = tss[1]

        self.assertEqual(ts_copy.key, ts_orig.key)
        self.assertEqual(ts_copy.frequency, ts_orig.frequency)
        self.assertTrue(np.array_equal(ts_copy.tseries, ts_orig.tseries))
        self.assertTrue(np.array_equal(ts_copy.dseries, ts_orig.dseries))
        self.assertListEqual(ts_copy.columns, ts_orig.columns)
        self.assertEqual(ts_copy.end_of_period, ts_orig.end_of_period)

        ts_orig = self.tss[2]
        ts_copy = tss[2]

        self.assertEqual(ts_copy.key, ts_orig.key)
        self.assertEqual(ts_copy.frequency, ts_orig.frequency)
        self.assertTrue(np.array_equal(ts_copy.tseries, ts_orig.tseries))
        self.assertTrue(np.array_equal(ts_copy.dseries, ts_orig.dseries))
        self.assertListEqual(ts_copy.columns, ts_orig.columns)
        self.assertEqual(ts_copy.end_of_period, ts_orig.end_of_period)

    def test_as_dict(self):
        "Can it return a dict from the list?"

        self.assertTrue(ValueError, self.tss.as_dict)

        test_dict = {}
        for i in range(len(self.tss)):
            ts = self.tss[i]
            ts.key = 'key_%i' % (i)
            test_dict[ts.key] = ts

        self.assertDictEqual(self.tss.as_dict(), test_dict)

    def test_tsslist_do_func(self):
        pass


if __name__ == '__main__':
    unittest.main()
