# ZenPacks.daviswr.OSX.Server.Caching

ZenPack to model & monitor the Caching Service in OS X Server

## Requirements

* Apple OS X 10.8 or later with the Server package from the App Store
  * Only tested with Server 5 (Yosemite & El Capitan) so far...
* An account on the OS X host, which can
  * Log in via SSH with a key
  * Run the `serveradmin` command with "settings" and "fullstatus" parameters without password

Example entries in /etc/sudoers

```
Cmnd_Alias SERVERADMIN_FULLSTATUS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin fullstatus *
Cmnd_Alias SERVERADMIN_SETTINGS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin settings *
zenoss ALL=(ALL) NOPASSWD: SERVERADMIN_FULLSTATUS, SERVERADMIN_SETTINGS
```

## Usage

I'm not going to make any assumptions about your device class organization, so it's up to you to configure the `daviswr.cmd.OSXCachingService` modeler on the appropriate class or device.
