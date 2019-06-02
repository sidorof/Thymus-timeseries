Helpers
=======

A brief explanation of some helper classes.

When dealing with a set of timeseries, it can be useful to gather them
into groups that have some commonality, such as lists and dicts. Both
classes are derived from the list and dict objects with additional
features added.

TssList
-------

This class starts with the list class and adds some features to smooth
the path for using sets of timeseries. It is called TssList to suggest
the plural of timeseries (ts).

To use it we will start with three sample timeseries.

::

        start_date = datetime(2015, 12, 31).toordinal()

        ts = Timeseries()
        ts.key = 'One'
        ts.dseries = start_date + np.arange(10)
        ts.tseries = np.arange(10)
        ts.make_arrays()

        # longer timeseries
        ts_long = Timeseries()
        ts_long.key = 'Two'
        ts_long.dseries = start_date + np.arange(20)
        ts_long.tseries = np.arange(20)
        ts_long.make_arrays()

        # shorter timeseries
        ts_short = Timeseries()
        ts_short.key = 'Three'
        ts_short.dseries = start_date + np.arange(5)
        ts_short.tseries = np.arange(5)
        ts_short.make_arrays()

Having created the timeseries' for our set, now we create our aggregate
list.

::


        tsslist = TssList([
            ts,
            ts_long,
            ts_short
        ])

Having created our list we will see some features available to us that
are not found with a normal list.

min\_date() and max\_date()
---------------------------

With disparate timeseries, it can be helpful to know where the
timeframes start and end, particularly when truncating or doing
operations on them as a group.

combine(discard=True, pad=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function operates essentially in the same fashion as the combine
function for an individual timeseries.

For our example:

::

        # discard is True, truncate to match the shortest timeseries
        ts = tsslist.combine(discard=True, pad=None)

        # the shape matches the shortest timeseries but with all three columns
        print(ts.tseries.shape)
        (5, 3)

        # do not discard, instead pad with zeros
        ts = tsslist.combine(discard=False, pad=0)

        # the shape matches the longest timeseries
        print(ts.tseries.shape)
        (20, 3)

get\_values(date, notify=False)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This function finds the values as of a particular date and so does not
require either explicitly walking the list of timeseries, or combining
the timeseries into a common timeseries to get the values.

The notify flag indicates whether an error is thrown if a date is not
present in one of the timeseries. If notify is false, a None is inserted
where the value would be.

clone()
~~~~~~~

This function operates in the same fashion as the clone function for an
individual timeseries.

as\_dict()
~~~~~~~~~~

Sometimes it is helpful to flip a list to a dict to work with specific
timeseries directly. as\_dict() returns a dict with the keys being the
key for each timeseries.

TssDict
-------

This class provides similar features to TssList and is designed to be
used when using specific timeseries or groups of timeseries.

We will create a sample version.

::

        tssdict = TssDict(
            [
                ts,
                ts_long,
                ts_short
            ])

The keys for the dict will be the key for the timeseries. You can also
do have lists of timeseries. For example we can add to our tssdict:

::

        tssdict['our_list'] = [
            Timeseries(),
            Timeseries(),
            Timeseries()]

        anew_tssdict = TssDict()

        # a dict in the dict
        tssdict['anew'] = anew_tssdict

Why the last one? Not really sure, but it could be done. But when you
start doing turtles all the way the down, it could get problematical.

As with TssList, there are similar functions available aside from the
usual functions associated with a dict.

min\_date(), max\_date()
~~~~~~~~~~~~~~~~~~~~~~~~

These functions operate in the same way as TssList with an important
difference.

::

        min_date, key = tssdict.min_date()

        max_date, key = tssdict.max_date()

With this version you can know which key has the value.

get\_values(date, keys=None, notify=False)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This version of get\_values, like the TssList returns values found in
the timeseries as of a particular date. However, you can pass in a list
of which keys to select as well as the order returned of the values.

::

        values, keys = tssdict.get_values(date, keys=None, notify=False)

If the keys option is None, all the keys returned in whatever order the
dict decides to use.

combine(keys=None, discard=True, pad=None)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This version of combine, like the TssList combines all the timeseries
into one timeseries. It uses the same options, except as in the previous
function, you can pass in a list of keys to govern the order of the
columns in the timeseries.

If the value portion of the dict is a list, TssList, or TssDict, that
value portion will be combined into a timeseries before being appended
to the timeseries in common.

clone()
~~~~~~~

This function returns a copy of the object as the others do.
