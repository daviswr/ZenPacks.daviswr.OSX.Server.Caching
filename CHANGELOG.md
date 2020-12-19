# Change Log

## [Unreleased]

## [1.1.1] - 2020-12-19
### Fixed
 * Minor event transform updates

## [1.1.0] - 2018-07-22
Delete Caching Service components from devices monitored by this ZenPack or the devices themselves, then remove the previous version before installing this version. Class names have changed in keeping with Apple's nomenclature.

### Added
 * Support for macOS 10.13 High Sierra's `AssetCacheManagerUtil`

### Fixed
 * Package count datapoint uses modeled "DataPath" value rather than the static default path

### Changed
 * Internal class and relationship names

## [1.0.0] - 2018-07-15
This release does **_not_** support High Sierra or Mojave.

Any previous version of this ZenPack should be removed before installing this one, due to the added peer server relationship.
### Added
 * Improved error state events
 * Cache packaage count
 * Process monitoring
 * Peer server components

### Changed
 * Requires ZenPackLib 2.0+
 * Using CommandPlugin modeling and ZenCommand collection again

### Removed
 * PythonPlugin-based modeler

## [0.9.2] - 2017-01-19
Final ZenPackLib 1.x release
### Added
 * Thresholds for status-related datapoints

### Changed
 * Acitivity graph units from bits/min to bits/sec
 * Component display tweaks

### Removed
 * Removed old CommandPlugin-based modeler

## [0.9.1] - 2016-08-15
### Changed
 * ZenPackLib 1.0.13
 * Monitoring template honors zCommandPort for SSH port

### Fixed
 * "Use SSH" setting

## [0.9.0] - 2016-08-14
### Changed
 * Using PythonPlugin modeler instead of CommandPlugin to work around OpenSSH 6.9 in OS X 10.11

## [0.8.2] - 2016-06-17
### Changed
 * Language delimiter in Cache ID

## 0.8.1 - 2016-06-14
 * Alpha release

[Unreleased]: https://github.com/daviswr/ZenPacks.daviswr.OSX.Server.Caching/compare/1.1.1...HEAD
[1.1.1]: https://github.com/daviswr/ZenPacks.daviswr.OSX.Server.Caching/compare/1.1.0...1.1.1
[1.1.0]: https://github.com/daviswr/ZenPacks.daviswr.OSX.Server.Caching/compare/1.0.0...1.1.0
[1.0.0]: https://github.com/daviswr/ZenPacks.daviswr.OSX.Server.Caching/compare/0.9.2...1.0.0
[0.9.2]: https://github.com/daviswr/ZenPacks.daviswr.OSX.Server.Caching/compare/0.9.1...0.9.2
[0.9.1]: https://github.com/daviswr/ZenPacks.daviswr.OSX.Server.Caching/compare/0.9.0...0.9.1
[0.9.0]: https://github.com/daviswr/ZenPacks.daviswr.OSX.Server.Caching/compare/0.8.2...0.9.0 
[0.8.2]: https://github.com/daviswr/ZenPacks.daviswr.OSX.Server.Caching/compare/0.8.1...0.8.2
