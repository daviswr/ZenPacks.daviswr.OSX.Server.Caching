# ZenPacks.daviswr.OSX.Server.Caching

ZenPack to model & monitor the Caching Service in OS X Server

## Requirements

* Apple OS X 10.8 or later with the Server package from the App Store
  * Tested with:
    * Server 5.0 on OS X 10.10 Yosemite
    * Server 5.1 on OS X 10.11 El Capitan
    * Server 5.2 on macOS 10.12 Sierra
* An account on the OS X host, which can
  * Log in via SSH with a key
  * Run the `serveradmin` command with "settings" and "fullstatus" parameters without password

Example entries in /etc/sudoers

```
Cmnd_Alias SERVERADMIN_FULLSTATUS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin fullstatus *
Cmnd_Alias SERVERADMIN_SETTINGS = /Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin settings *
zenoss ALL=(ALL) NOPASSWD: SERVERADMIN_FULLSTATUS, SERVERADMIN_SETTINGS
```

## El Capitan & Later Issues

El Capitan ships with OpenSSH 6.9 and disables Diffie-Hellman key exchanges with SHA-1 hashes, which the version of Twisted Conch, and thus ZenCommand, in Zenoss 4.2.5 SP671 (not tried 5.x) requires. These can be re-enabled, but...

OpenSSH appears to have deprecated SSH2_MSG_KEX_DH_GEX_REQUEST_OLD (type 30) key exchanges [in 2015](https://anongit.mindrot.org/openssh.git/commit/?id=318be28cda1fd9108f2e6f2f86b0b7589ba2aed0) and Conch [was updated](https://twistedmatrix.com/trac/ticket/8100), but Conch in Zenoss 4.2.5 SP671 only supports that message type.

This has been worked around by changing the modeler from a CommandPlugin to PythonPlugin which calls the host system's `ssh` command. zProperties `zKeyPath`, `zCommandPort`, and `zCommandUsername` are still required, however.

## Usage

I'm not going to make any assumptions about your device class organization, so it's up to you to configure the `daviswr.python.OSXCachingService` modeler on the appropriate class or device.
