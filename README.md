# ZenPacks.daviswr.OSX.Server.Caching

ZenPack to model & monitor the Caching Service in OS X Server

## Requirements

* Apple OS X 10.8 or later with the Server package from the App Store
  * Tested with:
    * Server 5.0 on OS X 10.10 Yosemite
    * Server 5.1 on OS X 10.11 El Capitan
    * Server 5.2 on OS X 10.11 El Capitan
    * Server 5.2 on macOS 10.12 Sierra
* An account on the OS X host, which can
  * Log in via SSH with a key
  * Run the `serveradmin` command with "settings" and "fullstatus" parameters without password

Example entries in /etc/sudoers

```
Cmnd_Alias SERVERADMIN_FULLSTATUS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin fullstatus *
Cmnd_Alias SERVERADMIN_SETTINGS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin settings *
Cmnd_Alias LS_CACHEDATA = /bin/ls /Library/Server/Caching/Data/
zenoss ALL=(ALL) NOPASSWD: SERVERADMIN_FULLSTATUS, SERVERADMIN_SETTINGS, LS_CACHEDATA
```

## El Capitan & Later Issues

This requires Zenoss 4.2.5 SP732 or later (including 5+) to support the newer versions of OpenSSH shipped with OS X 10.11 El Capitan and later macOS releases.

## Usage

I'm not going to make any assumptions about your device class organization, so it's up to you to configure the `daviswr.cmd.OSXCachingService` modeler on the appropriate class or device.
