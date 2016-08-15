import os
from Products.DataCollector.plugins.CollectorPlugin \
    import PythonPlugin
from Products.DataCollector.plugins.DataMaps \
    import MultiArgs, RelationshipMap, ObjectMap
import subprocess

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
        log.info(
            "Modeler %s processing data for device %s",
            self.name(), device.id)
        maps = list()

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
                if not caches.has_key(idx):
                  caches[idx] = dict()
                caches[idx].update({k: v})
            else:
                k = key.split(':')[1]
                service.update({k: output.get(key).replace('"', '')})

        # Caching Service
        for boolean in ['Active', 'AllowPersonalCaching', \
            'LocalSubnetsOnly', 'LogClientIdentity', 'RestrictedMedia']: 
            if service.has_key(boolean):
                service[boolean] = True if ('yes' == service[boolean]) else False

        for numeric in ['CacheFree', 'CacheLimit', 'CacheUsed', \
            'Port', 'ReservedVolumeSpace']:
            if service.has_key('numeric'):
                service[numeric] = int(service[numeric])

        service['id'] = self.prepId('CachingService')
        service['title'] = service.get('ServerRoot',
            service.get('DataPath', 'Caching Service'))
        # Not listening, service likely not running
        if service.has_key('Port') and service.get('Port') == 0:
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
            if cache.has_key('BytesUsed'):
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
