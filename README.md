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
* An account on the macOS host, which can
  * Log in via SSH with a key
    * RSA or EC required for macOS 10.13+
  * Run `ls` on the "DataPath" returned by `serveradmin settings caching` or `AssetCacheManagerUtil settings`, with a trailing `/` character for compatibility with previous examples.
    * Default path on 10.13 is `/Library/Application\ Support/Apple/AssetCache/Data/` 
  * Server only: Run the `serveradmin` command with "settings" and "fullstatus" parameters without password

Example entries in /etc/sudoers
```
Cmnd_Alias SERVERADMIN_FULLSTATUS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin fullstatus *
Cmnd_Alias SERVERADMIN_SETTINGS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin settings *
Cmnd_Alias LS_CACHEDATA = /bin/ls /Library/Server/Caching/Data/
zenoss ALL=(ALL) NOPASSWD: SERVERADMIN_FULLSTATUS, SERVERADMIN_SETTINGS, LS_CACHEDATA
```
 * `serveradmin` lines not required on macOS 10.13+
 * `LS_CACHEDATA` target path needs to match the 

## SSH Issues

This ZenPack requires Zenoss 4.2.5 SP732 or later (including 5+) to support the newer versions of OpenSSH shipped with OS X 10.11 El Capitan and later macOS releases.

As of macOS 10.13 High Sierra, DSA keys are no longer supported for SSH authentication. You may need to generate new keys.

## Usage

I'm not going to make any assumptions about your device class organization, so it's up to you to configure the ~~`daviswr.cmd.OSXCachingService`~~ `daviswr.cmd.macOSContentCache` modeler on the appropriate class or device.
