# ZenPacks.daviswr.OSX.Server.Caching

ZenPack to model & monitor the Content Caching Service in macOS

## Requirements

* Apple OS X 10.8 or later with the Server package from the App Store
  * Tested with:
    * OS X 10.10 Yosemite with Server 5.0
    * OS X 10.11 El Capitan with Server 5.1
    * OS X 10.11 El Capitan with Server 5.2
    * macOS 10.12 Sierra with Server 5.2
    * macOS 10.13 High Sierra
    * macOS 10.14 Mojave
* An account on the macOS host with sudo permission, which can:
  * Log in via SSH with a key
    * RSA or EC required for macOS 10.13+
  * Run `ls` on the "DataPath" returned by `serveradmin settings caching` or `AssetCacheManagerUtil settings`, with a trailing `/` character for compatibility with previous examples.
    * Default path on 10.13+ is `/Library/Application\ Support/Apple/AssetCache/Data/`
    * Prior default path is `/Library/Server/Caching/Data/`
  * Open `AssetInfo.db` in the "DataPath" directory with `sqlite3`
  * Server only: Run the `serveradmin` command with "settings" and "fullstatus" parameters without password
* [ZenPackLib](https://help.zenoss.com/in/zenpack-catalog/open-source/zenpacklib)

### Example entries in /etc/sudoers

Up to 10.12 Sierra
```
Cmnd_Alias SERVERADMIN_FULLSTATUS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin fullstatus caching
Cmnd_Alias SERVERADMIN_SETTINGS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin settings caching
Cmnd_Alias LS_CACHEDATA = /bin/ls /Library/Server/Caching/Data/
Cmnd_Alias ASSETINFO_DB = /usr/bin/sqlite3 -cmd .timeout\ * -line file\:/Library/Server/Caching/Data/AssetInfo.db?mode=ro *
zenoss ALL=(ALL) NOPASSWD: SERVERADMIN_FULLSTATUS, SERVERADMIN_SETTINGS, LS_CACHEDATA, ASSETINFO_DB
```

10.13 High Sierra and later
```
Cmnd_Alias LS_CACHEDATA = /bin/ls /Library/Application\ Support/Apple/AssetCache/Data/
Cmnd_Alias ASSETINFO_DB = /usr/bin/sqlite3 -cmd .timeout\ * -line file\:/Library/Application\ Support/Apple/AssetCache/Data/AssetInfo.db?mode=ro *
zenoss ALL=(ALL) NOPASSWD: LS_CACHEDATA, ASSETINFO_DB
```

## SSH Issues

This ZenPack requires Zenoss 4.2.5 SP732 or later (including 5+) to support the newer versions of OpenSSH shipped with OS X 10.11 El Capitan and later macOS releases.

As of macOS 10.13 High Sierra, DSA keys are no longer supported for SSH authentication. You may need to generate new keys.

## Usage

I'm not going to make any assumptions about your device class organization, so it's up to you to configure the ~~`daviswr.cmd.OSXCachingService`~~ `daviswr.cmd.macOSContentCache` modeler on the appropriate class or device.
