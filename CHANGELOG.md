# Changelog
## (0.2.4)
* Changed the function `TsProto.common_length`. Previously, accepted two timeseries and returned two timeseries that trimmed to the length in common those timeseries. Now, it accepts a list of timeseries via `*ts`.
* Corrected some wording in function docs.

## (0.2.3) -
### Added
* Added a minor improvement to how headers are treated when using `Timeseries.to_dict()`. Outputting a dictionary version of a Timeseries consists of header and data. The header previously consisted of the elements key, columns, frequency, and end_of_period. Now, the header function outputs any elements in self.__dict__ that are not tseries and dseries. Any subclasses of Timeseries with extra fields will now be included automatically.

