"""
This module tests the TssList class
"""
import unittest

from datetime import date, datetime, timedelta
import json
import numpy as np


from src.timeseries import Timeseries
from src.tsslist import TssList
from src.tssdict import TssDict


class TestTssDict(unittest.TestCase):
    """This class tests the class TssDict."""

    def setUp(self):
        # three timeseries
        self.ts = Timeseries()
        self.ts.key = "Main"
        self.ts.columns = ["F1"]

        start_date = datetime(2015, 12, 31).toordinal()
        self.ts.dseries = start_date + np.arange(10)
        self.ts.tseries = np.arange(10)
        self.ts.make_arrays()

        # longer timeseries
        self.ts_long = Timeseries()
        self.ts_long.key = "Long"
        start_date = datetime(2015, 12, 31).toordinal()
        self.ts_long.dseries = start_date + np.arange(20)
        self.ts_long.tseries = np.arange(20)
        self.ts_long.make_arrays()

        # shorter timeseries
        self.ts_short = Timeseries()
        self.ts_short.key = "Short"
        start_date = datetime(2015, 12, 31).toordinal()
        self.ts_short.dseries = start_date + np.arange(5)
        self.ts_short.tseries = np.arange(5)
        self.ts_short.make_arrays()

        self.tssdict = TssDict([self.ts, self.ts_long, self.ts_short])

    def test_class_init_(self):
        """Test class initialization."""

        self.assertEqual(len(self.tssdict), 3)

        tmp_ts0 = Timeseries()
        tmp_ts1 = Timeseries()
        tmp_ts2 = Timeseries()

        tmp_ts0.key = "ts0"
        tmp_ts1.key = "ts1"
        tmp_ts2.key = "ts2"

        tssdict = TssDict([tmp_ts0, tmp_ts1, tmp_ts2])

        self.assertEqual(len(tssdict), 3)

        tssdict = TssDict()

        tssdict["ts0"] = tmp_ts0
        tssdict["ts1"] = tmp_ts1
        tssdict["ts2"] = tmp_ts2

        self.assertEqual(len(tssdict), 3)

        tssdict = TssDict(
            {
                tmp_ts0.key: tmp_ts0,
                tmp_ts1.key: tmp_ts1,
                tmp_ts2.key: tmp_ts2,
            }
        )

        self.assertEqual(len(tssdict), 3)

    def test_tssdict_from_split_ts(self):
        ts = Timeseries()

        ts.tseries = np.arange(100).reshape((10, 10))
        ts.dseries = date.today().toordinal() + np.arange(10)

        self.assertRaises(ValueError, TssDict.split_timeseries, ts)

        ts.columns = [f"Col{i}" for i in range(5)]

        self.assertRaises(ValueError, TssDict.split_timeseries, ts)

        ts.columns = [f"Col{i}" for i in range(10)]

        tssdict = TssDict(split=ts)

        self.assertListEqual(list(tssdict.keys()), ts.columns)

        for idx, (key, ts_tmp) in enumerate(tssdict.items()):
            self.assertListEqual(ts.dseries.tolist(), ts_tmp.dseries.tolist())

            self.assertListEqual(
                ts.tseries[:, idx].tolist(), ts_tmp.tseries.flatten().tolist()
            )

            self.assertEqual(ts.columns[idx], ts_tmp.columns[0])

    def test_tssdict_min_date(self):
        """Tests min date"""

        # First add a timeseries that is earlier than the others
        tmp_ts0 = Timeseries()
        tmp_ts0.key = "First"

        tmp_ts0.dseries = datetime(2014, 12, 31).toordinal() - np.arange(10)
        tmp_ts0.tseries = np.arange(10)
        tmp_ts0.make_arrays()

        self.tssdict[tmp_ts0.key] = tmp_ts0

        self.assertTupleEqual(
            self.tssdict.min_date(), (date(2014, 12, 22), "First")
        )

        tmp_nodata = Timeseries()
        tmp_nodata.key = "nothing"
        tssdict = TssDict()
        tssdict[tmp_nodata.key] = tmp_nodata

        self.assertTupleEqual(tssdict.min_date(), (None, "nothing"))

        tssdict = TssDict()

        # none timeseries list
        tssdict["test"] = [
            date(2014, 12, 31) + timedelta(days=i) for i in range(10)
        ]
        tssdict["test1"] = [
            date(2013, 12, 31) + timedelta(days=i) for i in range(10)
        ]
        self.assertRaises(ValueError, tssdict.min_date)

    def test_tssdict_max_date(self):
        """Tests max date"""

        self.assertTupleEqual(
            self.tssdict.max_date(), (date(2016, 1, 19), "Long")
        )

        tssdict = TssDict()

        # none timeseries list
        tssdict["test"] = [
            date(2014, 12, 31) + timedelta(days=i) for i in range(10)
        ]
        tssdict["test1"] = [
            date(2013, 12, 31) + timedelta(days=i) for i in range(10)
        ]
        self.assertRaises(ValueError, tssdict.max_date)

    def test_tssdict_longest_ts(self):
        """
        This test tests for the longest timeseries.
        """
        length, key = self.tssdict.longest_ts()

        self.assertTupleEqual(
            (length, key), (self.ts_long.tseries.shape[0], "Long")
        )

        self.tssdict["test"] = "something else"
        self.assertRaises(ValueError, self.tssdict.longest_ts)

    def test_tssdict_shortest_ts(self):
        """
        This test tests for the shortest timeseries.
        """
        length, key = self.tssdict.shortest_ts()

        self.assertTupleEqual(
            (length, key), (self.ts_short.tseries.shape[0], "Short")
        )

        # zero length
        self.tssdict["nothing"] = Timeseries()
        self.assertIsNone(self.tssdict.shortest_ts())

        del self.tssdict["nothing"]

        # bad data
        self.tssdict["bad"] = "something else"
        self.assertRaises(ValueError, self.tssdict.shortest_ts)

    def test_tssdict_combine(self):
        """
        A batch of tests combining columns to one timeseries.

        Tests check to see whether the parameters are passed down properly to
        each timeseries.
        """

        # combine(self, discard=True, pad=None)
        ts_new, _ = self.tssdict.combine(discard=True, pad=None)

        # shape corresponds to the shortest length
        self.assertEqual(
            ts_new.tseries.shape[0], self.ts_short.tseries.shape[0]
        )

        self.assertEqual(ts_new.tseries.shape[1], 3)

        # combine(self, discard=False, pad=0)
        ts_new, _ = self.tssdict.combine(discard=False, pad=0)

        # shape corresponds to the longest length
        self.assertEqual(
            ts_new.tseries.shape[0], self.ts_long.tseries.shape[0]
        )

        self.assertEqual(ts_new.tseries.shape[1], 3)

        # test with TssList
        tmp_ts0 = Timeseries()
        tmp_ts0.key = "First"

        tmp_ts0.dseries = datetime(2014, 12, 31).toordinal() - np.arange(10)
        tmp_ts0.tseries = np.arange(10)
        tmp_ts0.make_arrays()

        tmp_ts1 = Timeseries()
        tmp_ts1.key = "Second"

        tmp_ts1.dseries = datetime(2014, 12, 31).toordinal() - np.arange(10)
        tmp_ts1.tseries = np.arange(10)
        tmp_ts1.make_arrays()

        tssdict = TssDict(TssList([tmp_ts0, tmp_ts1]))

        ts, _ = tssdict.combine()

        self.assertTupleEqual(ts.tseries.shape, (10, 2))

        # test with TssDict
        tssdict = TssDict(TssDict([tmp_ts0, tmp_ts1]))

        ts, _ = tssdict.combine()
        self.assertTupleEqual(ts.tseries.shape, (10, 2))

    def test_tssdict_get_values(self):
        """Tests the ability to locate the correct row of data."""

        date1 = datetime(2016, 1, 4)  # existing date within date series
        date2 = datetime(2016, 1, 16)  # date falling on a weekend

        # get data from existing date
        self.assertTupleEqual(
            self.tssdict.get_values(
                date=date1, keys=["Main", "Long", "Short"]
            ),
            ((4.0, 4.0, 4.0), ("Main", "Long", "Short")),
        )

        # attempt to get data from date not present, with notify
        self.assertRaises(
            ValueError, self.tssdict.get_values, date2, notify=True
        )

        # attempt to get data from date not present, no notify
        self.assertTupleEqual(
            self.tssdict.get_values(
                date=date2, keys=["Main", "Long", "Short"]
            ),
            ((None, 16.0, None), ("Main", "Long", "Short")),
        )

    def test_clone(self):
        """Verifies that a copy is made."""
        tssdict = self.tssdict.clone()

        # is it a separate object
        for key, ts_new in tssdict.items():
            ts_orig = self.tssdict[key]
            self.assertNotEqual(ts_new, ts_orig)

        # do the characteristics match up?
        self.assertEqual(len(tssdict), 3)

    def test_to_json(self):
        """
        This function tests sending a TssList to a json format.

        Using a cheap assumption that since it is simply a dict, that as long
        as the timeseries are converted, the list is what is needed to check.

        More needs to be checked.
        """

        json_str = self.tssdict.to_json()

        self.assertIsInstance(json.loads(json_str), dict)

    def test_from_dict(self):
        """
        This function tests creating a TssDict instance from a dict of timeseries.

        The format of the incoming timeseries is to_dict(dt_fmt='str')
        """
        tssdict = TssDict().from_dict(
            {
                self.ts.key: self.ts.to_dict(dt_fmt="str"),
                self.ts_long.key: self.ts_long.to_dict(dt_fmt="str"),
                self.ts_short.key: self.ts_short.to_dict(dt_fmt="str"),
            }
        )
        self.assertListEqual(
            list(self.tssdict.keys()),
            [self.ts.key, self.ts_long.key, self.ts_short.key],
        )

    def test_from_json(self):
        """
        This function tests building back a tsslist from json fmt string.

        This relies heavily on the test for Timeseries.from_json.
        """
        json_str = self.tssdict.to_json()

        tssdict = TssDict()

        tssdict.from_json(json_str)

        self.assertEqual(len(tssdict), 3)

        self.assertTupleEqual(tssdict["Main"].shape(), self.ts.shape())
        self.assertTupleEqual(tssdict["Long"].shape(), self.ts_long.shape())
        self.assertTupleEqual(tssdict["Short"].shape(), self.ts_short.shape())

        test = json.dumps(["test"])

        self.assertRaises(ValueError, tssdict.from_json, json.dumps(["test"]))

    def test_tssdict_do_func(self):
        """Placeholder for future function."""
        pass


if __name__ == "__main__":
    unittest.main()
