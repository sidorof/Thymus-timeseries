# tests/test_point.py
"""
This module tests the Point class
"""
import unittest

from datetime import date, datetime
import json
import numpy as np

from thymus.timeseries import Timeseries
from thymus.point import Point


class TestPoint(unittest.TestCase):
    """This class tests the class Point."""

    def setUp(self):
        # three timeseries
        self.ts = Timeseries()
        self.ts.key = "Test Key"
        self.ts.columns = ["dog", "cat", "squirrel"]

        self.start_date = datetime(2021, 1, 29).toordinal()
        self.ts.dseries = self.start_date + np.arange(5)
        self.ts.tseries = np.arange(15).reshape((5, 3)) / 10.33
        self.ts.make_arrays()

    def test_class_init_(self):
        """Test class initialization."""
        point = Point(self.ts, 3)

        self.assertTrue(hasattr(point, "dog"))
        self.assertTrue(hasattr(point, "cat"))
        self.assertTrue(hasattr(point, "squirrel"))

        self.assertEqual(point.dog, point.values[0])
        self.assertEqual(point.cat, point.values[1])
        self.assertEqual(point.squirrel, point.values[2])
        self.assertEqual(point.date, point.ts.dseries[3])
        self.assertEqual(point.row_no, 3)

        point.dog = 1
        point.cat = 2
        point.squirrel = 3

        self.assertEqual(point.dog, point.values[0])
        self.assertEqual(point.cat, point.values[1])
        self.assertEqual(point.squirrel, point.values[2])

    def test__repr__(self):
        """Test the appearance."""
        point = Point(self.ts, 3)

        output = repr(point)

        self.assertTrue(output.startswith("<Point"))
        self.assertTrue(output.endswith("/>"))

        for column in self.ts.columns:
            with self.subTest(column=column):
                self.assertTrue(output.find(column) > -1)

        # no columns
        self.ts.columns = None
        point = Point(self.ts, 3)

        output = repr(point)

        # has values
        self.assertTrue(output.find("[") > -1)

        # should show new name
        class NewPoint(Point):
            def __init__(self, ts, row_no):
                super().__init__(ts, row_no)

        output = repr(NewPoint(self.ts, 3))

        self.assertTrue(output.startswith("<NewPoint"))
        self.assertTrue(output.endswith("/>"))

        # format question
        ts = self.ts[:, 1]
        point = Point(ts, 3)

        self.assertEqual(
            repr(point),
            "<Point: row_no: 3, date: 2021-02-01, 0.968054211035818 />",
        )

        ts.columns = ["test"]
        point = Point(ts, 3)

        self.assertEqual(
            repr(point),
            "<Point: row_no: 3, date: 2021-02-01, test: 0.968054211035818 />",
        )

    def test_to_dict(self):
        """Test formatting for a dictionary."""

        # native date format
        self.assertDictEqual(
            Point(self.ts, 3).to_dict(),
            {
                "row_no": 3,
                "date": datetime(2021, 1, 29).toordinal() + 3,
                "dog": 0.8712487899322362,
                "cat": 0.968054211035818,
                "squirrel": 1.0648596321393997,
            },
        )

        # str date format
        self.assertDictEqual(
            Point(self.ts, 0).to_dict(dt_fmt="str"),
            {
                "row_no": 0,
                "date": datetime(2021, 1, 29).strftime("%F"),
                "dog": 0.0,
                "cat": 0.0968054211035818,
                "squirrel": 0.1936108422071636,
            },
        )

        # str date format
        self.assertDictEqual(
            Point(self.ts, 0).to_dict(dt_fmt="datetime"),
            {
                "row_no": 0,
                "date": datetime(2021, 1, 29).date(),
                "dog": 0.0,
                "cat": 0.0968054211035818,
                "squirrel": 0.1936108422071636,
            },
        )

        # invalid date format
        self.assertRaises(ValueError, Point(self.ts, 0).to_dict, dt_fmt="test")


if __name__ == "__main__":
    unittest.main()
