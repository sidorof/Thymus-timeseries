# Thymus-Timeseries

An intuitive library tracking dates and timeseries in common using numpy
arrays.

When working with arrays of timeseries, the manipulation process can easily cause mismatching sets of arrays in time, arrays in the wrong order, slow down the analysis, and lead to generally spending more time to ensure consistency.

This library attempts to address the problem in a way that enables ready access to the current date range, but stays out of your way most of the time. Essentially, this library is a wrapper around numpy arrays.

This library grew out of the use of market and trading data. The timeseries is typically composed of regular intervals but with gaps such as weekends and holidays. In the case of intra-day data, there are interuptions due to periods when the market is closed or gaps in trading.

While the library grew from addressing issues associated with market data, the implementation does not preclude use in other venues. Direct access to the numpy arrays is expected and the point of being able to use the library.

## Dependencies

Other than NumPy being installed, there are no other requirements.

## Installation

```pip install thymus-timeseries```

## A Brief Look at Capabilities.

### Creating a Small Sample Timeseries Object

As a first look, we will create a small timeseries object and show a few ways
that it can used. For this example, we will use daily data.

from datetime import datetime
import numpy as np

from thymus.timeseries import Timeseries

ts = Timeseries()

#### Elements of Timeseries()

* **key:**  An optional identifier for the timeseries.
* **columns:** Defaults to None but is an an optional list of column names for the data.
* **frequency:** Defaults to `d`, the **d** in this case refers to the default daily data. current frequencies supported are `sec`, `min`, `h`, `d`, `w`, `m`, `q`, `y`.

* **dseries:** This is a numpy array of dates in numeric format.

* **tseries:** This is a numpy array of data. most of the work takes place here.

* **end-of-period:**  Defaults to True indicating that the data is as of the end of the period. This only comes into play when converting from one frequency to another and will be ignored for the moment.


While normal usage of the timeseries object would involve pulling data from a database and inserting data into the timeseries object, we will use a quick-and-dirty method of inputting some data. Dates are stored as either ordinals or timestamps, avoiding clogging up memory with large sets of datetime objects. Because it is daily data, ordinals will be used for this example.
```
ts = Timeseries()

start_date = datetime(2015, 12, 31).toordinal()

ts.dseries = start_date + np.arange(10)
ts.tseries = np.arange(10)

ts.make_arrays()
```
We created an initial timeseries object. It starts at the end of 2015 and continues for 10 days. Setting the values in **dseries** and **tseries** can be somewhat sloppy. For example, a list could be assigned initially to either **dseries** (the dates) and a numpy array to **tseries** (the values).

The use of the **make_arrays()** function converts the date series to an int32 array (because they are ordinal values) and **tseries** to a float64 array. The idea is that the data might often enter the timeseries object as lists, but then be converted to arrays of appropriate format for use.

The completed timeseries object is:
```
    print(ts)

    <Timeseries>
    key:
    columns: None
    frequency: d
    daterange: ('2015-12-31', '2016-01-09')
    end-of-period: True
    shape: (10,)
```
You can see the date range contained in the date series. The shape refers to the shape of the **tseries** array. **key** and **columns** are free-form, available to update as appropriate to identify the timeseries and content of the columns. Again, the **end-of-period** flag can be ignored right now.

## Selection

Selection of elements is the same as numpy arrays. Currently, our sample has
10 elements.
```
    print(ts[:5])

    <Timeseries>
    key:
    columns: []
    frequency: d
    daterange: ('2015-12-31', '2016-01-04')
    end-of-period: True
    shape: (5,)
```
Note how the date range above reflects the selected elements.
```
ts1 = ts % 2 == 0
ts1.tseries
[True False True False True False True False True False]
```
We can isolate the dates of even numbers: note that `tseries`, not the timeseries obj, is explicitly used with `np.argwhere`.  More on when to operate directly on tseries later.
```
evens = np.argwhere((ts % 2 == 0).tseries)

ts_even = ts[evens]
```
This just prints a list of date and value pairs only useful with very small sets (or examples like this)
```
print(ts_even.items('str'))

('2015-12-31', '[0.0]')
('2016-01-02', '[2.0]')
('2016-01-04', '[4.0]')
('2016-01-06', '[6.0]')
('2016-01-08', '[8.0]')
```

### Date-based Selection

So let us use a slightly larger timeseries. 1000 rows 2 columns of data. And,
use random values to ensure uselessness.
```
    ts = Timeseries()

    start_date = datetime(2015, 12, 31).toordinal()

    ts.dseries = start_date + np.arange(1000)
    ts.tseries = np.random.random((1000, 2))

    ts.make_arrays()

    print(ts)

    <Timeseries>
    key:
    columns: []
    frequency: d
    daterange: ('2015-12-31', '2018-09-25')
    end-of-period: True
    shape: (1000, 2)
```

You can select on the basis of date ranges, but first we will use a row number
technique that is based on slicing. This function is called **trunc()** for
truncation.

#### Normal Truncation
You will end up with a timeseries with row 100 through 499. This provides in-place execution.
```
ts.trunc(start=100, finish=500)

# this version returns a new timeseries, effective for chaining.
ts1 = ts.trunc(start=100, finish=500, new=True)
```
#### Truncation by Date Range
But suppose you want to select a specific date range? This leads to the next
function, **truncdate()**.
```
    # select using datetime objects
    ts1 = ts.truncdate(
        start=datetime(2017, 1, 1),
        finish=datetime(2017, 12, 31),
        new=True)

    print(ts1)

    <Timeseries>
    key:
    columns: []
    frequency: d
    daterange: ('2017-01-01', '2017-12-31')
    end-of-period: True
    shape: (365, 2)
```
As you might expect, the timeseries object has a date range of all the days
during 2017. But see how this is slightly different than slicing. When you use
`truncdate()` it selects everything within the date range *inclusive* of the
ending date as well. The idea is to avoid having to always find one day after
the date range that you want to select to accommodate slicing behavior. This
way is more convenient in this context.

You can also convert data from a higher frequency to a lower frequency. Suppose we needed monthly data for 2017 from our timeseries.

```
start = datetime(2017, 1, 1)
finish = datetime(2017, 12, 31)
ts1 = ts.truncdate(start=start, finish=finish, new=True).convert('m')

print(ts1.items('str'))

('2017-01-31', '[0.1724835781570483, 0.9856812220255055]')
('2017-02-28', '[0.3855043513164875, 0.30697511661843124]')
('2017-03-31', '[0.7067982987769881, 0.7680886691626396]')
('2017-04-30', '[0.07770763295126926, 0.04697651222041588]')
('2017-05-31', '[0.4473657194650975, 0.49443624153533783]')
('2017-06-30', '[0.3793816656495891, 0.03646544387811124]')
('2017-07-31', '[0.2783335012003322, 0.5144979569785825]')
('2017-08-31', '[0.9261879195281345, 0.6980224313957553]')
('2017-09-30', '[0.09531834159018227, 0.5435208082899813]')
('2017-10-31', '[0.6865842769906441, 0.7951735180348887]')
('2017-11-30', '[0.34901775001111657, 0.7014208950555662]')
('2017-12-31', '[0.4731393617405252, 0.630488855197775]')
```

Or yearly. In this case, we use a flag that governs whether to include the partial period leading up to the last year. The default includes it. However, when unwanted the flag, **include_partial** can be set to False.
```
ts1 = ts.convert('y', include_partial=True)

print(ts1.items('str'))

('2015-12-31', '[0.2288539210230056, 0.288320541664724]')
('2016-12-31', '[0.5116274142615629, 0.21680312154651182]')
('2017-12-31', '[0.4731393617405252, 0.630488855197775]')
('2018-09-25', '[0.7634145837512148, 0.32026411425902257]')

ts2 = ts.convert('y', include_partial=False)

print(ts2.items('str'))

('2015-12-31', '[[0.2288539210230056, 0.288320541664724]]')
('2016-12-31', '[[0.5116274142615629, 0.21680312154651182]]')
('2017-12-31', '[[0.4731393617405252, 0.630488855197775]]')
```

## Points
Sometimes when examining a `tseries`, a particular point stands out and you want to investigate it further. When was it? Since this package separates dates and values by design, there needs to be a quick way to find this out.

There are two ways to do this. Suppose the value in question is row 100.
```
row = 100
# would give you the ordinal/timestamp date
ts.dseries[row]

# gives a datetime object.
datetime.fromordinal(ts.dseries[row])
```
This is not particularly difficult, but you do enough times, it feels laborious. To cut down on the typing, there is another way.
```
Usage:
    get_point(rowdate=None, row_no=None)

row = 100
point = ts.get_point(row_no=100)

print(point)

<Point: row_no: 100, date: 2020-04-10, [48.3886577  48.48543501 48.58221233 48.67898964 48.77576696] />

```
This gives all the information in one place, the row number, a meaningful date, and the values of interest.

The point object created contains attributes:
* **ts:** The originating timeseries.
* **row_no:** The location within the data.
* **date:** This ordinal/timestamp in the data
* **date_str:** This method shows the date in string format.
* **datetime:** This method shows the date as datetime object.
* **values:** The values contained in the row.

Note that the `Point` class is designed to be an active window into your data. Changing an item in values is a direct change to the timeseries.

Changing the `row_no` shifts contents of `values` to reflect the data in the new row.

### Columns
If you use columns in your timeseries, you can also improve your output.
```
ts.columns = ["dog", "cat", "squirrel", "cow", "monkeys"]

print(point)

<Point: row_no: 100, date: 2020-04-10,
  dog: 48.38865769863544
  cat: 48.48543501403271
  squirrel: 48.58221232942998
  cow: 48.678989644827254
  monkey: 48.77576696022452 />
```
The point object uses the columns of the timeseries to create attributes.

The point object now has created the following attributes:
* **ts:** The originating timeseries.
* **row_no:** The location within the data.
* **date:** This ordinal/timestamp in the data
* **date_str:** This method shows the date in string format.
* **datetime:** This method shows the date as  datetime object.
* **values:** The values contained in the row.

New Attributes:

* **dog:** Column 0
* **cat:** Column 1
* **squirrel:** Column 2
* **cow:** Column 3
* **monkey:** Column 4

Just as `values` is a direct window, these attributes are also a direct window. Changing `point.dog` affects the `tseries[row_no][0]` value.

With just a few columns of data, it is not hard to remember which is which. However, more columns become increasingly unwieldy.

### Iteration
Because the `Point` class automatically changes as the row number changes, it can also be used for iteration. A subclassed Point can provide easy programmatic access for calculations and updates with meaningful variable names.

## Combining Timeseries

Suppose you want to combine multiple timeseries together that are of different lengths? In this case we assume that the two timeseries end on the same date, but one has a longer tail than the other. However, the operation that you need requires common dates.

By **combine** we mean instead of two timeseries make one timeseries that has
the columns of both.
```
    ts_short = Timeseries()
    ts_long = Timeseries()

    end_date = datetime(2016, 12, 31)

    ts_short.dseries = [
            (end_date + timedelta(days=-i)).toordinal()
            for i in range(5)]

    ts_long.dseries = [
            (end_date + timedelta(days=-i)).toordinal()
            for i in range(10)]

    ts_short.tseries = np.zeros((5))
    ts_long.tseries = np.ones((10))

    ts_short.make_arrays()
    ts_long.make_arrays()

    ts_combine = ts_short.combine(ts_long)

    print(ts.items('str'))

    ('2016-12-31', '[0.0, 1.0]')
    ('2016-12-30', '[0.0, 1.0]')
    ('2016-12-29', '[0.0, 1.0]')
    ('2016-12-28', '[0.0, 1.0]')
    ('2016-12-27', '[0.0, 1.0]')
```
The combine function has a couple variations. While it can be helpful to automatically discard the unwanted rows, you can also enforce that combining does not take place if the number of rows do not match. Also, you can build out the missing information with padding to create a timeseries that has
the length of the longest timeseries.
```
# this would raise an error -- the two are different lengths
ts_combine = ts_short.combine(ts_long discard=False)

# this combines, and fills 99 as a missing value
ts_combine = ts_short.combine(ts_long discard=False, pad=99)

print(ts_combine.items('str'))
('2016-12-31', '[0.0, 1.0]')
('2016-12-30', '[0.0, 1.0]')
('2016-12-29', '[0.0, 1.0]')
('2016-12-28', '[0.0, 1.0]')
('2016-12-27', '[0.0, 1.0]')
('2016-12-26', '[99.0, 1.0]')
('2016-12-25', '[99.0, 1.0]')
('2016-12-24', '[99.0, 1.0]')
('2016-12-23', '[99.0, 1.0]')
('2016-12-22', '[99.0, 1.0]')
```
The combining can also receive multiple timeseries.
```
ts_combine = ts_short.combine([ts_long, ts_long, ts_long])

print(ts_combine.items('str'))
('2016-12-31', '[0.0, 1.0, 1.0, 1.0]')
('2016-12-30', '[0.0, 1.0, 1.0, 1.0]')
('2016-12-29', '[0.0, 1.0, 1.0, 1.0]')
('2016-12-28', '[0.0, 1.0, 1.0, 1.0]')
('2016-12-27', '[0.0, 1.0, 1.0, 1.0]')
```
## Splitting Timeseries

In some ways it would make sense to mirror the **combine()** function
with a **split()** from an aesthetic standpoint. However, splitting is very
straight-forward without such a function. For example, suppose you want a
timeseries that only has the the first two columns from our previous example.
As you can see in the ts_split tseries, the first two columns were taken.
```
    ts_split = ts_combine[:, :2]

    print(ts_split.items('str'))
    ('2016-12-31', '[0.0, 1.0]')
    ('2016-12-30', '[0.0, 1.0]')
    ('2016-12-29', '[0.0, 1.0]')
    ('2016-12-28', '[0.0, 1.0]')
    ('2016-12-27', '[0.0, 1.0]')
```

## Arithmetic Operations

We have combined timeseries together to stack up rows in common. In
addition, we looked at the issue of mismatched lengths. Now we will look at
arithmetic approaches and some of the design decisions and tradeoffs associated
with mathematical operations.

We will start with the **add()** function. First, if we assume that all we are
adding together are arrays that have exactly the same dateseries, and
therefore the same length, and we assume they have exactly the same number of
columns, then the whole question becomes trivial. If we relax those
constraints, then some choices need to be made.

We will use the long and short timeseries from the previous example.
```
    # this will fail due to dissimilar lengths
    ts_added = ts_short.add(ts_long, match=True)

    # this will work
    ts_added = ts_short.add(ts_long, match=False)

    [ 1.  1.  1.  1.  1.  1.  1.  1.  1.  1.]
```
The **add()** function checks to see if the number of columns match. If they do
not an error is raised. If the **match** flag is True, then it also checks
that all the dates in both timeseries match prior to the operation.

If **match** is False, then as long as the columns are compatible, the
operation can take place. It also supports the concept of sparse arrays as
well. For example, suppose you have a timeseries that is primary, but you would
like to add in a timeseries values from only a few dates within the range. This
function will find the appropriate dates adding in the values at just those
rows.

To summarize, all dates in common to both timeseries will be included in the
new timeseries if **match** is False.

Because the previous function is somewhat specialized, you can assume that the
checking of common dates and creating the new timeseries can be somewhat slower
than other approaches.

If we assume some commonalities about our timeseries, then we can do our work
in a more intuitive fashion.

### Assumptions of Commonality

Let us assume that our timeseries might be varying in length, but we absolutely
know what either our starting date or ending date is. And, let us assume that
all the dates for the periods in common to the timeseries match.

If we accept those assumptions, then a number of operations become quite easy.

The timeseries object can accept simple arithmetic as if it is an array. It
automatically passes the values on to the **tseries** array. If the two arrays
are not the same length the longer array is truncated to the shorter length. So
if you were add two arrays together that end at the same date, you would want
to sort them latest date to earliest date using the function
**sort_by_date()**.

### Examples
```
# starting tseries
ts.tseries
[ 0.  1.  2.  3.  4.  5.  6.  7.  8.  9.]

(ts + 3).tseries
[  3.   4.   5.   6.   7.   8.   9.  10.  11.  12.]

# Also, reverse (__radd__)
(3 + ts).tseries
[  3.   4.   5.   6.   7.   8.   9.  10.  11.  12.]

# of course not just addition
5 * ts.tseries
[  0.   5.  10.  15.  20.  25.  30.  35.  40.  45.]
```
Also, in-place operations. But first, we will make a copy.
```
ts1 = ts.clone()
ts1.tseries /= 3
print(ts1.tseries)
[0.0
0.3333333333333333
0.6666666666666666
1.0
1.3333333333333333
1.6666666666666667
2.0
2.3333333333333335
2.6666666666666665
3.0]

ts1 = ts ** 3
ts1.tseries
0.0
1.0
8.0
27.0
64.0
125.0
216.0
343.0
512.0
729.0

ts1 = 10 ** ts
ts1.tseries
[1.0
10.0
100.0
1000.0
10000.0
100000.0
1000000.0
10000000.0
100000000.0
1000000000.0]
```

In other words, the normal container functions you can use with numpy arrays
are available to the timeseries objects. The following container functions for
arrays are supported.
```
__pow__ __add__ __rsub__ __sub__    __eq__      __ge__   __gt__   __le__
__lt__  __mod__ __mul__  __ne__     __radd__    __rmod__ __rmul__ __rpow__
__abs__ __pos__ __neg__  __invert__ __rdivmod__ __rfloordiv__
__floordiv__ __truediv__
__rtruediv__ __divmod__

__and__ __or__ __ror__ __rand__ __rxor__ __xor__ __rshift__
__rlshift__ __lshift__ __rrshift__

__iadd__ __ifloordiv__ __imod__ __imul__ __ipow__ __isub__
__itruediv__]

__iand__ __ilshift__ __ior__ __irshift__ __ixor__
```
### Functions of Arrays Not Supported

The purpose the timeseries objects is to implement an intuitive usage of
timeseries objects in a fashion that is consistent with NumPy. However, it is
not intended to replace functions that are better handled explicitly with
the **dseries** and **tseries** arrays directly. The difference will be clear
by comparing the list of functions for the timeseries object versus a numpy array. Most of the functions of the timeseries object is related to handling the commonality of date series with time series. You can see that the bulk of the thymus functions relate to maintenance of the coordination betwee the date series and timeseries. The meat of the functions still lie with the
numpy arrays by design.

```
# timeseries members and functions:
ts.add                   ts.daterange             ts.get_pcdiffs           ts.series_direction
ts.as_dict               ts.datetime_series       ts.header                ts.set_ones
ts.as_json               ts.dseries               ts.if_dseries_match      ts.set_zeros
ts.as_list               ts.end_date              ts.if_tseries_match      ts.shape
ts.clone                 ts.end_of_period         ts.items                 ts.sort_by_date
ts.closest_date          ts.extend                ts.key                   ts.start_date
ts.columns               ts.fmt_date              ts.lengths               ts.trunc
ts.combine               ts.frequency             ts.make_arrays           ts.truncdate
ts.common_length         ts.get_date_series_type  ts.months                ts.tseries
ts.convert               ts.get_datetime          ts.replace               ts.years
ts.date_native           ts.get_diffs             ts.reverse
ts.date_string_series    ts.get_duped_dates       ts.row_no

# numpy functions in the arrays
ts.tseries.T             ts.tseries.cumsum        ts.tseries.min           ts.tseries.shape
ts.tseries.all           ts.tseries.data          ts.tseries.nbytes        ts.tseries.size
ts.tseries.any           ts.tseries.diagonal      ts.tseries.ndim          ts.tseries.sort
ts.tseries.argmax        ts.tseries.dot           ts.tseries.newbyteorder  ts.tseries.squeeze
ts.tseries.argmin        ts.tseries.dtype         ts.tseries.nonzero       ts.tseries.std
ts.tseries.argpartition  ts.tseries.dump          ts.tseries.partition     ts.tseries.strides
ts.tseries.argsort       ts.tseries.dumps         ts.tseries.prod          ts.tseries.sum
ts.tseries.astype        ts.tseries.fill          ts.tseries.ptp           ts.tseries.swapaxes
ts.tseries.base          ts.tseries.flags         ts.tseries.put           ts.tseries.take
ts.tseries.byteswap      ts.tseries.flat          ts.tseries.ravel         ts.tseries.tobytes
ts.tseries.choose        ts.tseries.flatten       ts.tseries.real          ts.tseries.tofile
ts.tseries.clip          ts.tseries.getfield      ts.tseries.repeat        ts.tseries.tolist
ts.tseries.compress      ts.tseries.imag          ts.tseries.reshape       ts.tseries.tostring
ts.tseries.conj          ts.tseries.item          ts.tseries.resize        ts.tseries.trace
ts.tseries.conjugate     ts.tseries.itemset       ts.tseries.round         ts.tseries.transpose
ts.tseries.copy          ts.tseries.itemsize      ts.tseries.searchsorted  ts.tseries.var
ts.tseries.ctypes        ts.tseries.max           ts.tseries.setfield      ts.tseries.view
ts.tseries.cumprod       ts.tseries.mean          ts.tseries.setflags
```
### Other Date Functions

Variations on a theme:
```
# truncation
ts.truncdate(
    start=datetime(2017, 1, 1),
    finish=datetime(2017, 12, 31))

# just start date etc.
ts.truncdate(
    start=datetime(2017, 1, 1))

# this was in date order but suppose it was in reverse order?
# this result will give the same answer
ts1 = ts.truncdate(
    start=datetime(2017, 1, 1),
    new=True)

ts.reverse()

ts1 = ts.truncdate(
    start=datetime(2017, 1, 1),
    new=True)

# use the date format native to the dateseries (ordinal / timestamp)
ts1 = ts.truncdate(
    start=datetime(2017, 1, 1).toordinal(),
    new=True)

# suppose you start with a variable that represents a date range
# date range can be either a list or tuple
ts.truncdate(
    [datetime(2017, 1, 1), datetime(2017, 12, 31)])
```
## Assorted Date Functions
```
# native format
ts.daterange()
(735963, 735972)

# str format
ts.daterange('str')
('2015-12-31', '2016-01-09')

# datetime format
ts.daterange('datetime')
(datetime.datetime(2015, 12, 31, 0, 0), datetime.datetime(2016, 1, 9, 0, 0))

# native format
ts.start_date(); ts.end_date()
735963  735972

# str format
ts.start_date('str'); ts.end_date('str')
2015-12-31  2016-01-09

# datetime format
ts.start_date('datetime'); ts.end_date('datetime')
2015-12-31 00:00:00  2016-01-09 00:00:00
```
Sometimes it is helpful to find a particular row based on the date. Also, that date might not be in the dateseries, and so, the closest date will suffice.

We will create a sample timeseries to illustrate.
```
ts = Timeseries()
ts.dseries = []
ts.tseries = []

start_date = datetime(2015, 12, 31)
for i in range(40):
    date = start_date + timedelta(days=i)
    if date.weekday() not in [5, 6]:   # skipping weekends

        ts.dseries.append(date.toordinal())
        ts.tseries.append(i)

ts.make_arrays()

# row_no, date
(0, '2015-12-31')
(1, '2016-01-01')
(2, '2016-01-04')
(3, '2016-01-05')
(4, '2016-01-06')
(5, '2016-01-07')
(6, '2016-01-08')
(7, '2016-01-11')
(8, '2016-01-12')
(9, '2016-01-13')
(10, '2016-01-14')
(11, '2016-01-15')
(12, '2016-01-18')
(13, '2016-01-19')
(14, '2016-01-20')
(15, '2016-01-21')
(16, '2016-01-22')
(17, '2016-01-25')
(18, '2016-01-26')
(19, '2016-01-27')
(20, '2016-01-28')
(21, '2016-01-29')
(22, '2016-02-01')
(23, '2016-02-02')
(24, '2016-02-03')
(25, '2016-02-04')
(26, '2016-02-05')
(27, '2016-02-08')

date1 = datetime(2016, 1, 7)    # existing date within date series
date2 = datetime(2016, 1, 16)   # date falling on a weekend
date3 = datetime(2015, 6, 16)   # date prior to start of date series
date4 = datetime(2016, 3, 8)    # date after to end of date series

# as datetime and in the series
existing_row = ts.row_no(rowdate=date1, closest=1)
5

existing_date = ts.closest_date(rowdate=date1, closest=1)
print(datetime.fromordinal(existing_date))
2016-01-07 00:00:00

# as datetime but date not in series
next_row = ts.row_no(rowdate=date2, closest=1)
12

next_date = ts.closest_date(rowdate=date2, closest=1)
print(datetime.fromordinal(next_date))
2016-01-18 00:00:00

prev_row = ts.row_no(rowdate=date2, closest=-1)
11

prev_date = ts.closest_date(rowdate=date2, closest=-1)
print(datetime.fromordinal(prev_date))
2016-01-15 00:00:00

# this will fail -- date is outside the date series
# as datetime but date not in series, look for earlier date
ts.closest_date(rowdate=date3, closest=-1)

# this will fail -- date is outside the date series
ts.closest_date(rowdate=date4, closest=1)
```
## Functions by Category

### Output

#### Timeseries
##### **ts.to_dict()**

Returns the time series as a dict with the date as the key.

Usage:
    self.to_dict(dt_fmt=None, data_list=False)

This has been reworked to include all fields of the timeseries
rather than just dates and times, so header informtion is now included.

For flexibility, the date can be formatted in various ways:
* dt_fmt=None Native format depending on frequency                         but converted to string.
* dt_fmt='datetime' Datetime objects.
* dt_fmt='str' Converts dates to string using constants                         `timeseries.FMT_DATE` or `timeseries.FMT_IDATE`, depending on the timeseries type.

* data_list A boolean that signals whether dates should be used as keys in a dict for the values, or whether the dates and values are output as a list.

This matters because some operations are necessary to target
specific dates, but it does not preserve order. Or, if data_list
is True, then the combination of dates and values are output as
a list and order is maintained.

##### **ts.to_json()**

This function returns the timeseries in JSON format.

Usage:
    self.as_json(indent=2, dt_fmt=str, data_list=True)

dt_fmt options are the same as for to_dict

##### **ts.to_list()**

Returns the timeseries as a list.

#### Point
##### **point.to_dict()**
This function returns a dict of the point variables.

Usage:
    to_dict(dt_fmt=None)

Parameters:
    dt_fmt: (None|str) : Format choice is "str" or "datetime"

Returns:
    point (dict)

Typical output:
```
point.to_dict(dt_fmt="str")

{
  "row_no": 100,
  "date": "2020-04-10",
  "dog": 48.38865769863544,
  "cat": 48.48543501403271,
  "squirrel": 48.58221232942998,
  "cow": 48.678989644827254,
  "monkeys": 48.77576696022452
}

```

### Miscellaneous
#### ts.header()

This function returns a dict of the non-timeseries data.

#### ts.items(fmt=None)

This function returns the date series and the time series as if it
is in one list. The term items used to suggest the iteration of dicts
where items are the key, value combination.

if fmt == 'str':
    the dates are output as strings

#### ts.months(include_partial=True)

This function provides a quick way to summarize daily (or less)
as monthly data.

It is basically a pass-through to the convert function with more
decoration of the months.

Usage:

    months(include_partial=True)

    returns a dict with year-month as keys

#### ts.years(include_partial=True)

This function provides a quick way to summarize daily (or less)
as yearly data.

It is basically a pass-through to the convert function with more
decoration of the years.

Usage:

years(include_partial=True)

returns a dict with year as keys

#### ts.datetime_series()

This function returns the dateseries converted to a list of
datetime objects.

#### ts.date_string_series(dt_fmt=None)

This function returns a list of the dates in the timeseries as
strings.

Usage:
    self.date_string_series(dt_fmt=None)

dt_fmt is a datetime mask to alter the default formatting.

### Array Manipulation

#### ts.add(ts, match=True)

Adds two timeseries together.

if match is True:
    means there should be a one to one corresponding date in each time
    series.  If not raise error.
else:
    means that timeseries with sporadic or missing dates can be added

Note: this does not evaluate whether both timeseries have the same
        number of columns. It will fail if they do not.

Returns the timeseries. Not in-place.

#### ts.clone()

This function returns a copy of the timeseries.

#### ts.combine(tss, discard=True, pad=None)

This function combines timeseries into a single array. Combining in
this case means accumulating additional columns of information.

Truncation takes place at the end of rows. So if the timeseries is
sorted from latest dates to earliest dates, the older values would be
removed.

Usage:
    self.combine(tss, discard=True, pad=None)

Think of tss as the plural of timeseries.

If discard:
    Will truncate all timeseries lengths down to the shortest
    timeseries.

if discard is False:
    An error will be raised if the all the lengths do not match

    unless:
        if pad is not None:
            the shorter timeseries will be padded with the value pad.

Returns the new ts.

#### ts.common_length(*ts)

This static method trims the lengths of timeseries and returns the
timeseries trimmed to the same length.

The idea is that in order to do array operations there must be a
common length for each timeseries.

Reflecting the bias for using timeseries sorted from latest info to
earlier info, truncation takes place at the end of the array. That
way older less important values are removed if necessary.

Usage:
    ts1_new, ts2_new = self.common_length(ts1, ts2)
    [ts1, ts2, ..., ts_n] = self.common_length(*ts)

#### ts.convert(new_freq, include_partial=True, **kwargs)

This function returns the timeseries converted to another frequency,
such as daily to monthly.

Usage:
    convert(new_freq, include_partial=True, **kwargs)

The only kwarg is
    weekday=<some value>

This is used when converting to weekly data. The weekday number
corresponds to the the datetime.weekday() function.

#### ts.extend(ts, overlay=True)

This function combines a timeseries to another, taking into account the
possibility of overlap.

This assumes that the frequency is the same.

This function is chiefly envisioned to extend a timeseries with
additional dates.

Usage:
    self.extend(ts, overlay=True)

If overlay is True then the incoming timeseries will overlay
any values that are duplicated.

#### ts.trunc(start=None, finish=None, new=False)

This function truncates in place, typically.

truncate from (start:finish)
remember start is lowest number, latest date

This truncation works on the basis of slicing, so
finish is not inclusive.

Usage:
    self.trunc(start=None, finish=None, new=False)

#### ts.truncdate(start=None, finish=None, new=False)

This function truncates in place on the basis of dates.

Usage:
    self.truncdate(start=None, finish=None, new=False)

start and finish are dates, input as either datetime or the actual
internal format of the **dseries** (ordinals or timestamps).

If the dates are not actually in the list, the starting date will
be the next viable date after the start date requested. If the finish
date is not available, the previous date from the finish date will be
the last.

If new is True, the timeseries will not be modified in place. Rather
a new timeseries will be returned instead.

#### ts.replace(ts, match=True)

This function replaces values where the dates match an incoming
timeseries. So if the incoming date on the timeseries matches, the
value in the current timeseries will be replaced by the incoming
timeseries.

Usage:
    self.replace(ts, match=True)

If match is False, the incoming timseries may have dates not found in
the self timeseries.

Returns the modified timeseries. Not in place.

#### ts.reverse()

        This function does in-place reversal of the timeseries and dateseries.

#### ts.get_diffs()

This function gets the differences between values from date to date in
the timeseries.

#### ts.get_pcdiffs()

This function gets the percent differences between values in the
timeseries.

No provision for dividing by zero here.

#### ts.set_ones(fmt=None, new=False)

This function converts an existing timeseries to ones using the same
shape as the existing timeseries.

It is used as a convenience to create an empty timeseries with a
specified date range.

if fmt use as shape

usage:
    set_ones(self, fmt=None, new=False)

#### ts.set_zeros(fmt=None, new=False)

This function converts an existing timeseries to zeros using the same
shape as the existing timeseries.

It is used as a convenience to create an empty timeseries with a
specified date range.

if fmt use as shape

usage:
    set_zeros(self, fmt=None, new=False)

#### ts.sort_by_date(reverse=False, force=False)

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

### Evaluation

#### ts.daterange(fmt=None)

This function returns the starting and ending dates of the timeseries.

Usage:

    self.daterange()
        (735963, 735972)

    self.daterange('str')
        ('2015-12-31', '2016-01-09')

    self.daterange('datetime')
        (datetime(2015, 12, 31, 0, 0),
         datetime.datetime(2016, 1, 9, 0, 0))

#### ts.start_date(fmt=None)

This function returns the starting date of the timeseries in its
native value, timestamp or ordinal.

If fmt is 'str' returns in string format
If fmt is 'datetime' returns in string format

#### ts.end_date(fmt=None)

This funtcion returns the ending date of the timeseries in its native
value, timestamp or ordinal.

If fmt is 'str' returns in string format
If fmt is 'datetime' returns in string format

#### ts.get_duped_dates()

This function pulls dates that are duplicated. This is to be used to
locate timeseries that are faulty.

Usage:
    get_duped_dates()

    returns [[odate1, count], [odate2, count]]

#### ts.series_direction()

if a lower row is a lower date, then 1 for ascending
if a lower row is a higher date then -1 for descending

#### ts.get_date_series_type()

This function returns the date series type associated with the
timeseries.  The choices are TS_ORDINAL or TS_TIMESTAMP.

#### ts.if_dseries_match(ts)

This function returns True if the date series are the same.

#### ts.if_tseries_match(ts)

This function returns True if the time series are the same.

### Utilities

#### ts.date_native(date)

This awkwardly named function returns a date in the native format of the timeseries, namely ordinal or timestamp.

#### ts.row_no(rowdate, closest=0, no_error=False)

Shows the row in the timeseries

Usage:
    ts.row(rowdate=<datetime>)
    ts.row(rowdate=<date as either ordinal or timestamp>)

Returns an error if the date is not found in the index

if closest is invoked:
    closest = 1
        find the closest date after the rowdate
    closest = -1
        find the closest date before the rowdate

If no_error
    returns -1 instead of raising an error if the date was
    outside of the timeseries.

#### ts.get_datetime(date)

This function returns a date as a datetime object. This takes into account the type of date stored in **dseries**.

Usage:
    self.get_datetime(date)

#### ts.lengths()

This function returns the lengths of both the date series and time series. Both numbers are included in case a mismatch has occurred.

#### ts.shape()

This function return the shape of the timeseries. This is a shortcut
to putting in ts.tseries.shape.

#### ts.fmt_date(numericdate, dt_type, dt_fmt=None)

This static method accepts a date and converts it to the format used in the timeseries.

#### ts.make_arrays()

Convert the date and time series lists (if so) to numpy arrays

#### ts.get_fromDB(**kwargs)

This is just a stub to suggest a viable name for getting data from a database.

#### ts.save_toDB(**kwargs):

This is just a stub to suggest a viable name for saving data to a database.
