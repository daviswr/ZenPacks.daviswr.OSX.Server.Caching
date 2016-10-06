import os
import subprocess

from Products.DataCollector.plugins.CollectorPlugin \
    import PythonPlugin
from Products.DataCollector.plugins.DataMaps \
    import MultiArgs, RelationshipMap, ObjectMap

class OSXCachingService(PythonPlugin):
    req_properties = (
        'zKeyPath',
        'zCommandPort',
        'zCommandUsername',
        'manageIp',
        )

    deviceProperties = PythonPlugin.deviceProperties + req_properties

    def collect(self, device, log):
        # Command to run on monitored device.
        serveradmin = '/Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin'
        remote_cmd = '"sudo {0} settings caching; sudo {0} fullstatus caching"'.format(serveradmin)
        key_path = getattr(device, 'zKeyPath', '')
        cmd_port = getattr(device, 'zCommandPort', '')
        cmd_user = getattr(device, 'zCommandUsername', '')
        dev_ip = getattr(device, 'manageIp', '')
        ssh_path = '/usr/bin/ssh'
        ssh_params = '-o UserKnownHostsFile=/dev/null ' \
                     '-o StrictHostKeyChecking=no ' \
                     '-o PasswordAuthentication=no ' \
                     '-i {0} -l {1} -p {2} {3}'.format(key_path, cmd_user, cmd_port, dev_ip)
        command = '{0} {1} {2}'.format(ssh_path, ssh_params, remote_cmd)
        log.debug('Caching Service modeler command: %s', command)

        with open(os.devnull, 'w') as devnull:
            ps = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=devnull)
            output = ps.communicate()[0]

        return output

    def process(self, device, results, log):
        log.info('processing %s for device %s', self.name(), device.id)
        maps = list()

        """ Example output

        caching:ReservedVolumeSpace = 25000000000
        caching:LogClientIdentity = yes
        caching:CacheLimit = 70000000000
        caching:ServerRoot = "/Library/Server"
        caching:ServerGUID = "02FE97F2-41F3-4CEE-9899-27976DB91A1A"
        caching:DataPath = "/Library/Server/Caching/Data"
        caching:LocalSubnetsOnly = yes
        caching:Port = 0
        caching:CacheLimit = 70000000000
        caching:StartupStatus = "OK"
        caching:RegistrationStatus = 1
        caching:CacheFree = 52754638336
        caching:PersonalCacheUsed = 0
        caching:TotalBytesDropped = 0
        caching:CacheStatus = "OK"
        caching:TotalBytesStoredFromOrigin = 419351941
        caching:state = "RUNNING"
        caching:Port = 49232
        caching:Peers = _empty_array
        caching:TotalBytesStoredFromPeers = 0
        caching:RestrictedMedia = no
        caching:CacheDetails:_array_index:0:BytesUsed = 0
        caching:CacheDetails:_array_index:0:LocalizedType = "Mac Software"
        caching:CacheDetails:_array_index:0:MediaType = "Mac Software"
        caching:CacheDetails:_array_index:0:Language = "en"
        caching:CacheDetails:_array_index:1:BytesUsed = 419351941
        caching:CacheDetails:_array_index:1:LocalizedType = "iOS Software"
        caching:CacheDetails:_array_index:1:MediaType = "iOS Software"
        caching:CacheDetails:_array_index:1:Language = "en"
        ...
        caching:PersonalCacheLimit = 70000000000
        caching:CacheUsed = 419351941
        caching:TotalBytesStored = 419351941
        caching:TotalBytesImported = 0
        caching:PersonalCacheFree = 52754638336
        caching:Active = yes
        caching:TotalBytesReturned = 476014159
        """

        # Parse results
        output = dict(line.split(' = ') for line in results.splitlines())
        service = dict()
        caches = dict()
        for key in output:
            if key.startswith('caching:CacheDetails:'):
                short = key.replace('caching:CacheDetails:_array_index:', '')
                idx = int(short.split(':')[0])
                k = short.split(':')[1]
                v = output.get(key).replace('"', '')
                if idx not in caches:
                  caches[idx] = dict()
                caches[idx].update({k: v})
            else:
                k = key.split(':')[1]
                service.update({k: output.get(key).replace('"', '')})

        # Caching Service
        booleans = [
            'Active',
            'AllowPersonalCaching',
            'LocalSubnetsOnly',
            'LogClientIdentity',
            'RestrictedMedia',
            ]

        for attr in booleans:
            if attr in service:
                service[attr] = True if 'yes' == service[attr] else False

        integers = [
            'Active',
            'CacheFree',
            'CacheLimit',
            'CacheUsed',
            'Port',
            'ReservedVolumeSpace',
            ] 

        for attr in integers:
            if attr in service:
                service[attr] = int(service[attr])

        service['id'] = self.prepId('CachingService')
        service['title'] = service.get('ServerRoot',
            service.get('DataPath', 'Caching Service'))
        # Not listening, service likely not running
        if 'Port' in service and service.get('Port') == 0:
            del service['Port']
        log.debug('Caching Service\n%s', service)

        rm = RelationshipMap(
            relname='cachingService',
            modname='ZenPacks.daviswr.OSX.Server.Caching.CachingService'
            )
        rm.append(ObjectMap(
            modname='ZenPacks.daviswr.OSX.Server.Caching.CachingService',
            data=service
            ))
        maps.append(rm)

        # Individual Cache components
        rm = RelationshipMap(
            compname='cachingService/CachingService',
            relname='caches',
            modname='ZenPacks.daviswr.OSX.Server.Caching.Cache'
            )

        for idx in caches:
            cache = caches.get(idx)
            if 'BytesUsed' in cache:
                cache['BytesUsed'] = int(cache['BytesUsed'])
            lang = cache.get('Language', '')
            suffix = ' ({})'.format(lang) if (len(lang) > 0) else ''
            cache['id'] = self.prepId(cache.get('MediaType',
                'Cache {}'.format(str(idx))) \
                + '_' + lang)
            cache['title'] = cache.get('LocalizedType',
                cache.get('MediaType', 'Cache {}'.format(str(idx))) + 'suffix')
            log.debug('Individual Cache: %s', cache)
            rm.append(ObjectMap(
                modname='ZenPacks.daviswr.OSX.Server.Caching.Cache',
                data=cache
                ))
        maps.append(rm)

        return maps
