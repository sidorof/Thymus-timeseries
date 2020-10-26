# Changelog
## (0.2.3) -
### Added
* Added a minor improvement to how headers are treated when using `Timeseries.to_dict()`. Outputting a dictionary version of a Timeseries consists of header and data. The header previously consisted of the elements key, columns, frequency, and end_of_period. Now, the header function outputs any elements in self.__dict__ that are not tseries and dseries. Any subclasses of Timeseries with extra fields will now be included automatically.

