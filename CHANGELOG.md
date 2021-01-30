# Changelog
## (0.2.5)
### Added
* Added a Point class
This class enables a combined look at a specific point in a time series. While the purpose of Thymus-Timeseries is the separation of dates and values for more convenient processing, there are times when having
both together can be very useful.

Usage:
point = Point(ts, row)

This produces an object:

point.ts      a reference to the parent time series
point.row_no  the explicit row in the timeseries
point.date    ordinal/timestamp of the date
point.values  an array of values

If columns are being used for the object, properties
are created for each column / value pair.

For example:

```
    ts.columns = ["dog", "cat", "squirrel"]}

```

Properties will have
        point.dog
        point.cat
        point.squirrel

as well as values, as referenced above.

Setting point.dog to a new value will update the column in
`ts.tseries[row]`.

```
    print(point)
    <Point: row_no: 3, date: 2020-01-04,
      dog: 0.8709958385754379
      cat: 0.9677731539727088
      squirrel: 1.0645504693699797 />
```

* Added `get_point` function to Timeseries to enable easy access to the Point class described above.
This function gets both date and timeseries values for a particular row. It packages the results into an object. If the timeseries uses columns, those column names become object attributes.

This should be viewed as a window into a particular row. Updating the point values updates the timeseries row values.

Changing the row number on the point automatically updates the point for the new values.

A point object can therefore be used in an interation of timeseries as part of an updating process.

Usage:
    get_point(rowdate=None, row_no=None)

Parameters:
    rowdate: (None|int|float|datetime) : As with ts.row_no, the date can be either the ordinal/timestamp or datetime object.

    row_no: (None:int) : The row number of the timeseries.

    Either a rowdate or row_no must be selected.

Returns:
    point : (object) : Object of Point class

* Added `point_class` to the Timeseries object. This feature holds the default Point class used for the `get_point` described above. However, if a subclass of Point is created, then substituting in your own subclass will enable your custom Point class to be output.

* Added timeseries_class to both `TssList` and `TssDict`. When using subclassed `Timeseries`, both `TssList` and `TssDict` will automatically load

### Changed
* Added `timeseries_class` to both `TssList` and `TssDict`. When using the `from_json`, and `from_dict` functions in those classes, they now look to the class variable `timeseries_class`. This enables substituting your own version of the Timeseries class for use in those functions.
* Increased test coverage. Total coverage shows 93%.

## (0.2.4)
### Changed
* Changed the function `TsProto.common_length`. Previously, accepted two timeseries and returned two timeseries that trimmed to the length in common those timeseries. Now, it accepts a list of timeseries via `*ts`.
* Corrected some wording in function docs.

## (0.2.3) -
### Added
* Added a minor improvement to how headers are treated when using `Timeseries.to_dict()`. Outputting a dictionary version of a Timeseries consists of header and data. The header previously consisted of the elements key, columns, frequency, and end_of_period. Now, the header function outputs any elements in self.__dict__ that are not tseries and dseries. Any subclasses of Timeseries with extra fields will now be included automatically.

