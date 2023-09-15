"""
This module tests the prototype timeseries class.
"""
import unittest

from datetime import datetime
import numpy as np

from thymus.constants import FREQ_D, FREQ_SEC
from thymus.tsproto import TsProto
from thymus.tsslist import TssList


class TestTsProto(unittest.TestCase):
    """
    This class tests the base class TsProto.
    """

    def setUp(self):
        # three timeseries
        self.ts = TsProto()
        start_date = datetime(2015, 12, 31).toordinal()
        self.ts.dseries = start_date + np.arange(10)
        self.ts.tseries = np.arange(10)
        self.ts.make_arrays()

        # longer timeseries
        self.ts_long = TsProto()
        start_date = datetime(2015, 12, 31).toordinal()
        self.ts_long.dseries = start_date + np.arange(20)
        self.ts_long.tseries = np.arange(20)
        self.ts_long.make_arrays()

        # shorter timeseries
        self.ts_short = TsProto()
        start_date = datetime(2015, 12, 31).toordinal()
        self.ts_short.dseries = start_date + np.arange(5)
        self.ts_short.tseries = np.arange(5)
        self.ts_short.make_arrays()

    def test_class_init_(self):
        """Test class initialization."""
        tmp_ts = TsProto()

        # defaults for dseries, tseries might get changed back to list
        # self.assertIsInstance(tmp_ts.dseries, list)
        # self.assertIsInstance(tmp_ts.tseries, list)
        self.assertIsInstance(tmp_ts.columns, list)
        self.assertEqual(tmp_ts.frequency, FREQ_D)
        self.assertTrue(tmp_ts.end_of_period)

    def test_container_functions(self):
        """Tests the ability to pass through container functions to array."""

        ts = self.ts.clone()

        flist = [
            "__pow__",
            "__add__",
            "__rsub__",
            "__rtruediv__",
            "__divmod__",
            "__sub__",
            "__eq__",
            "__floordiv__",
            "__truediv__",
            "__ge__",
            "__gt__",
            "__le__",
            "__lt__",
            "__mod__",
            "__mul__",
            "__ne__",
            "__radd__",
            "__rdivmod__",
            "__rfloordiv__",
            "__rmod__",
            "__rmul__",
            "__rpow__",
        ]

        unary_flist = ["__abs__", "__pos__", "__neg__"]

        special_flist = ["__invert__"]

        flist1 = [
            "__and__",
            "__or__",
            "__ror__",
            "__rand__",
            "__rxor__",
            "__xor__",
            "__rshift__",
            "__rlshift__",
            "__lshift__",
            "__rrshift__",
        ]

        iflist = [
            "__iadd__",
            "__ifloordiv__",
            "__imod__",
            "__imul__",
            "__ipow__",
            "__isub__",
            "__itruediv__",
        ]

        iflist1 = [
            "__iand__",
            "__ilshift__",
            "__ior__",
            "__irshift__",
            "__ixor__",
        ]

        ts_other = self.ts.clone() * 4 + 3
        for func in flist:
            for other in [3, ts_other]:
                ts = self.ts.clone()
                ts.tseries += 1

                ts_a = getattr(ts, func)(other)
                a_series = ts_a.tseries

                if isinstance(other, TsProto):
                    b_series = getattr(ts.tseries, func)(other.tseries)
                else:
                    b_series = getattr(ts.tseries, func)(other)

                self.assertTrue(np.array_equal(a_series, b_series))
                self.assertTrue(ts.if_dseries_match(ts_a))

        # specific tests
        # decide what to do here. future warning that it will
        #    be eventually elementwise
        self.assertIsNotNone(ts_other)

        for func in unary_flist:
            ts = self.ts.clone()
            ts_a = getattr(ts, func)()
            a_series = ts_a.tseries

            b_series = getattr(ts.tseries, func)()

            self.assertTrue(np.array_equal(a_series, b_series))
            self.assertTrue(ts.if_dseries_match(ts_a))

        for func in special_flist:
            ts = self.ts.clone()
            ts.tseries = np.array(ts.tseries, np.int32)
            self.assertTrue(
                np.array_equal(
                    getattr(ts, func)().tseries,
                    getattr(ts.tseries, func)(),
                )
            )

        ts_other = self.ts.clone() * 4
        ts_other.tseries = np.array(ts_other.tseries, np.int64)
        for func in flist1:
            for other in [3, ts_other]:
                ts = self.ts.clone()
                ts.tseries = np.array(ts.tseries, np.int64)

                ts_a = getattr(ts, func)(other)
                a_series = ts_a.tseries

                if isinstance(other, TsProto):
                    b_series = getattr(ts.tseries, func)(other.tseries)
                else:
                    b_series = getattr(ts.tseries, func)(other)

                self.assertTrue(np.array_equal(a_series, b_series))
                self.assertTrue(ts.if_dseries_match(ts_a))

        for func in iflist:
            for other in [3, self.ts.clone() + 2.5]:
                ts = self.ts.clone() + 4.0
                ts1 = self.ts.clone() + 4.0

                ts_a = getattr(ts, func)(other)
                a_series = ts_a.tseries

                if isinstance(other, TsProto):
                    b_series = getattr(ts.tseries, func)(other.tseries)
                else:
                    b_series = getattr(ts.tseries, func)(other)

                self.assertTrue(np.array_equal(a_series, b_series))
                self.assertTrue(ts.if_dseries_match(ts_a))

        ts_other = self.ts.clone() * 4
        ts_other.tseries = np.array(ts_other.tseries, np.int64)
        for func in iflist1:
            for other in [3, ts_other]:
                ts = self.ts.clone()
                ts.tseries = np.array(ts.tseries, np.int64)
                ts1 = self.ts.clone()
                ts1.tseries = np.array(ts1.tseries, np.int64)

                if other is None:
                    other = self.ts.clone() * 4
                    other.tseries = np.array(other.tseries, np.int64)

                ts_a = getattr(ts, func)(other)
                a_series = ts_a.tseries

                if isinstance(other, TsProto):
                    b_series = getattr(ts.tseries, func)(other.tseries)
                else:
                    b_series = getattr(ts.tseries, func)(other)

                self.assertTrue(np.array_equal(a_series, b_series))
                self.assertTrue(ts.if_dseries_match(ts_a))

    def test_timeseries__add__lengths(self):
        """Tests adding two timeseries with mismatched lengths"""
        #
        # silently truncate
        ts1 = self.ts.clone()
        ts1.dseries = self.ts.dseries.tolist()[:5]
        ts1.tseries = self.ts.tseries.tolist()[:5]
        ts1.make_arrays()

        ts = self.ts + ts1

        self.assertEqual(ts.tseries[0], 0)
        self.assertEqual(ts.tseries[1], 2)
        self.assertEqual(ts.tseries[2], 4)
        self.assertEqual(ts.tseries[3], 6)
        self.assertEqual(ts.tseries[4], 8)

        self.assertEqual(len(ts.dseries), 5)
        self.assertEqual(len(ts.tseries), 5)

    def test_timeseries__add__columns(self):
        """Tests adding two timeseries mismatched columns"""
        ts1 = self.ts.clone()
        ts1.tseries = np.arange(10).reshape((-1, 1))
        ts1.make_arrays()

        # self ts shape   (10) incoming (10, 1)
        self.assertRaises(ValueError, self.ts.__add__, ts1)

        # self ts shape   (10, 1) incoming (10, 2)
        ts2 = ts1.clone()
        ts2.tseries = np.arange(20).reshape((-1, 2))
        ts2.make_arrays()

        self.assertRaises(ValueError, ts1.__add__, ts2)

    def test_timeseries__iadd__lengths(self):
        """Tests in-place adding two timeseries mismatched lengths"""
        #
        # silently truncate
        ts1 = self.ts.clone()
        ts1.dseries = self.ts.dseries.tolist()[:5]
        ts1.tseries = self.ts.tseries.tolist()[:5]
        ts1.make_arrays()

        self.ts += ts1

        self.assertEqual(self.ts.tseries[0], 0)
        self.assertEqual(self.ts.tseries[1], 2)
        self.assertEqual(self.ts.tseries[2], 4)
        self.assertEqual(self.ts.tseries[3], 6)
        self.assertEqual(self.ts.tseries[4], 8)

        self.assertEqual(len(self.ts.dseries), 5)
        self.assertEqual(len(self.ts.tseries), 5)

    def test_timeseries__iadd__columns(self):
        """Tests in-place adding two timeseries with mismatched columns"""
        ts1 = self.ts.clone()
        ts1.tseries = np.arange(10).reshape((-1, 1))
        ts1.make_arrays()

        # self ts shape   (10) incoming (10, 1)
        self.assertRaises(ValueError, self.ts.__iadd__, ts1)

        # self ts shape   (10, 1) incoming (10, 2)
        ts2 = ts1.clone()
        ts2.tseries = np.arange(20).reshape((-1, 2))
        ts2.make_arrays()

        self.assertRaises(ValueError, ts1.__iadd__, ts2)

    def test_column_checks(self):
        """Tests verification of similar columns"""
        ts1 = self.ts.clone()
        ts1.tseries = np.arange(10).reshape((-1, 1))
        ts1.make_arrays()

        # self ts shape   (10) incoming (10, 1)
        self.assertRaises(ValueError, self.ts._column_checks, self.ts, ts1)

        # self ts shape   (10, 1) incoming (10, 2)
        ts2 = ts1.clone()
        ts2.tseries = np.arange(20).reshape((-1, 2))
        ts2.make_arrays()

        self.assertRaises(ValueError, self.ts._column_checks, ts1, ts2)

        # now one with columns ok
        ts2 = ts1.clone()

        self.assertIsNone(self.ts._column_checks(ts1, ts2))

    def test_if_dseries_match(self):
        """Tests comparing two date series."""

        ts = self.ts.clone()

        self.assertTrue(self.ts.if_dseries_match(ts))

        ts = self.ts.clone()
        ts.dseries[0] += 1

        self.assertFalse(self.ts.if_dseries_match(ts))

    def test_if_tseries_match(self):
        """Tests comparing two series of values."""

        ts = self.ts.clone()

        self.assertTrue(self.ts.if_tseries_match(ts))

        ts = self.ts.clone()
        ts.tseries[0] += 1

        self.assertFalse(self.ts.if_tseries_match(ts))

    def test___getitem__(self):
        """This function tests selection."""

        ts = self.ts.clone()

        ts1 = ts[:2]

        self.assertTrue(np.array_equal(ts1.dseries, ts.dseries[:2]))
        self.assertTrue(np.array_equal(ts1.tseries, ts.tseries[:2]))

        # test separate slicing for dseries and tseries
        ts1 = ts.clone()

        ts1.tseries = np.arange(len(ts.tseries) * 4).reshape((-1, 4))

        ts2 = ts1[:5, 1]
        self.assertTrue(np.array_equal(ts2.dseries, ts1.dseries[:5]))
        self.assertTrue(np.array_equal(ts2.tseries, ts1.tseries[:5, 1]))

        # test separate slicing with more dimensions in tseries
        ts1 = TsProto()
        ts1.dseries = datetime(2016, 1, 1).toordinal() + np.arange(1000)

        ts1.tseries = np.arange(9000).reshape((1000, 3, 3))

        ts2 = ts1[:500, 1]

        self.assertTrue(np.array_equal(ts2.dseries, ts1.dseries[:500]))
        self.assertTrue(np.array_equal(ts2.tseries, ts1.tseries[:500, 1]))

        ts2 = ts1[:500, :, 1]

        self.assertTrue(np.array_equal(ts2.dseries, ts1.dseries[:500]))
        self.assertTrue(np.array_equal(ts2.tseries, ts1.tseries[:500, :, 1]))

        ts2 = ts1[:500, 1, :2]

        self.assertTrue(np.array_equal(ts2.dseries, ts1.dseries[:500]))
        self.assertTrue(np.array_equal(ts2.tseries, ts1.tseries[:500, 1, :2]))

    def test_timeseries_common_length(self):
        """Tests truncating timeseries to a common length."""

        ts1, ts2 = self.ts.common_length(self.ts, self.ts_long)
        self.assertEqual(len(ts1.tseries), len(ts2.tseries))

        ts1, ts2, ts3 = self.ts.common_length(
            self.ts, self.ts_short, self.ts_long
        )
        self.assertEqual(len(ts1.tseries), len(ts2.tseries))
        self.assertEqual(len(ts1.tseries), len(ts3.tseries))

    def test_timeseries_shape(self):
        """Tests returning the shape of the tseries."""

        self.assertTupleEqual(self.ts.shape(), self.ts.tseries.shape)

        ts = TsProto()

        # test blank TsProto
        ts = TsProto()
        self.assertIsNone(ts.shape(), None)

        # now with data
        ts.dseries = np.arange(100)
        ts.tseries = np.arange(200).reshape(100, 2)

        self.assertTupleEqual(ts.shape(), (ts.tseries.shape))

    def test_lengths(self):
        """Tests returning the lengths of the dseries and tseries."""

        lengths = self.ts.lengths()

        self.assertEqual(lengths[0], len(self.ts.dseries))
        self.assertEqual(lengths[1], len(self.ts.tseries))

        self.ts.tseries = self.ts.tseries[:3]

        lengths = self.ts.lengths()

        self.assertEqual(lengths[0], len(self.ts.dseries))
        self.assertEqual(lengths[1], len(self.ts.tseries))

    def test_timeseries_make_arrays(self):
        """Tests converting lists to arrays for both dseries and tseries."""

        # daily, so ordinal
        ts = TsProto()

        ts.frequency = FREQ_D

        ts.dseries = [i for i in range(100)]
        ts.tseries = [i for i in range(100)]

        ts.make_arrays()

        self.assertTrue(np.array_equal(ts.dseries, np.arange(100)))

        self.assertTrue(isinstance(ts.dseries[0], np.int32))
        self.assertTrue(isinstance(ts.tseries[0], np.float64))

        # seconds, so timestamp
        ts = TsProto()

        ts.frequency = FREQ_SEC

        ts.dseries = [i for i in range(100)]
        ts.tseries = [i for i in range(100)]

        ts.make_arrays()

        self.assertTrue(np.array_equal(ts.dseries, np.arange(100)))

        self.assertTrue(isinstance(ts.dseries[0], np.float64))
        self.assertTrue(isinstance(ts.tseries[0], np.float64))

        # verify that dseries is flattened
        ts.dseries = [[i] for i in range(100)]
        ts.tseries = [i for i in range(100)]

        ts.make_arrays()
        self.assertEqual(len(ts.dseries.shape), 1)

    def test_timeseries__make_array(self):
        """Tests making a numpy array to a specific type."""

        ts = TsProto()

        convert_list = [i for i in range(100)]

        new_array = ts._make_array(convert_list, numtype=np.float64)

        # verify structure, does not verify type
        self.assertTrue(np.array_equal(new_array, np.array(convert_list)))

        self.assertTrue(isinstance(new_array[0], np.float64))

        new_array = ts._make_array(convert_list, numtype=np.int32)

        self.assertTrue(np.array_equal(new_array, np.array(convert_list)))

        self.assertTrue(isinstance(new_array[0], np.int32))

    def test_timeseries_clone(self):
        """Tests creation of duplication timeseries."""

        ts = self.ts.clone()

        # is it a separate object
        self.assertNotEqual(ts.__str__(), self.ts.__str__())

        # do the characteristics match up?
        self.assertEqual(ts.key, self.ts.key)
        self.assertEqual(ts.frequency, self.ts.frequency)
        self.assertTrue(np.array_equal(ts.tseries, self.ts.tseries))
        self.assertTrue(np.array_equal(ts.dseries, self.ts.dseries))
        self.assertListEqual(ts.columns, self.ts.columns)
        self.assertEqual(ts.end_of_period, self.ts.end_of_period)


if __name__ == "__main__":
    unittest.main()
