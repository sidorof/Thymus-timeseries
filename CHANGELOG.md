# Changelog
## (0.3.5)
## Changed
* Corrected erroneous home page url.

## (0.3.4)
## Changed
* Updated packaging. Removed setup files. Now it only uses pyproject.toml.

## (0.3.1)
## Changed
* Corrected mistakes in packaging

## (0.3.0)
## Changed
* Updated packaging

## (0.2.6)
### Changed
* With a frequency conversion, if the asking frequency is the same as the current frequency, the return harmlessly returns the current timeseries.
### Added
* Added a parameter to TssDict for initializing with a parameter `split`, which can be timeseries with multiple columns. It then becomes a tssdict with each row becoming a separate timeseries, keyed on the column name.

## (0.2.5)
### Added
* Added a Point class
This class enables a combined look at a specific point in a time series.

* Added `get_point` function to Timeseries to enable easy access to the Point class described above.

* Added `point_class` to the Timeseries object. This feature holds the default Point class used for the `get_point` described above. However, if a subclass of Point is created, then substituting in your own subclass will enable your custom Point class to be output.

* Added `timeseries_class` to both `TssList` and `TssDict`. When using subclassed `Timeseries`, both `TssList` and `TssDict` will automatically load.

### Changed
* Increased test coverage. Total coverage shows 93%.

## (0.2.4)
### Changed
* Changed the function `TsProto.common_length`. Previously, accepted two timeseries and returned two timeseries that trimmed to the length in common those timeseries. Now, it accepts a list of timeseries via `*ts`.
* Corrected some wording in function docs.

## (0.2.3) -
### Added
* Added a minor improvement to how headers are treated when using `Timeseries.to_dict()`. Outputting a dictionary version of a Timeseries consists of header and data. The header previously consisted of the elements key, columns, frequency, and end_of_period. Now, the header function outputs any elements in self.__dict__ that are not tseries and dseries. Any subclasses of Timeseries with extra fields will now be included automatically.

