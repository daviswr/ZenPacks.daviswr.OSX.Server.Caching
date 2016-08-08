# ZenPacks.daviswr.OSX.Server.Caching

ZenPack to model & monitor the Caching Service in OS X Server

## Requirements

* Apple OS X 10.8 or later with the Server package from the App Store
  * Only tested with Server 5.0 on Yosemite so far...
  * See below regarding El Capitan & Server 5.1
* An account on the OS X host, which can
  * Log in via SSH with a key
  * Run the `serveradmin` command with "settings" and "fullstatus" parameters without password

Example entries in /etc/sudoers

```
Cmnd_Alias SERVERADMIN_FULLSTATUS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin fullstatus *
Cmnd_Alias SERVERADMIN_SETTINGS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin settings *
zenoss ALL=(ALL) NOPASSWD: SERVERADMIN_FULLSTATUS, SERVERADMIN_SETTINGS
```

## El Capitan Issues

OpenSSH that ships with El Capitan disabled Diffie-Hellman key exchanges with SHA-1 hashes, which the version of Twisted Conch, and thus ZenCommand, in Zenoss 4.2.5 SP671 (not tried 5.x) requires.

`/etc/ssh/ssh_config` has the line (commented out)
```
KexAlgorithms ecdh-sha2-nistp256,ecdh-sha2-nistp384,ecdh-sha2-nistp521,diffie-hellman-group-exchange-sha256,diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1,diffie-hellman-group1-sha1
```

Copying that to `/etc/ssh/sshd_config` and restarting the SSH daemon solves the kex algorithm mismatch, but results in the following message in /var/log/system.log:

```
error: Hm, kex protocol error: type 30 seq 1 [preauth]
``` 

Still working on that, any help would be appreciated...

## Usage

I'm not going to make any assumptions about your device class organization, so it's up to you to configure the `daviswr.cmd.OSXCachingService` modeler on the appropriate class or device.
