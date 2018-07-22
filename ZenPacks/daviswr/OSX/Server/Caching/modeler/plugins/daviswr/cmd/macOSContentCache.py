import json
from Products.DataCollector.plugins.CollectorPlugin \
    import CommandPlugin
from Products.DataCollector.plugins.DataMaps \
    import MultiArgs, RelationshipMap, ObjectMap


class macOSContentCache(CommandPlugin):
    # Command to run on monitored device.
    command = (
        'if [ -e "/usr/bin/AssetCacheManagerUtil" ];'
        'then '
        'cmd_base="/usr/bin/AssetCacheManagerUtil --json";'
        'settings_cmd="${cmd_base} settings 2>/dev/null";'
        'status_cmd="${cmd_base} status 2>/dev/null";'
        'else '
        'cmd_base="/usr/bin/sudo '
        '/Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin";'
        'settings_cmd="${cmd_base} settings caching";'
        'status_cmd="${cmd_base} fullstatus caching";'
        'fi;'
        'eval ${settings_cmd};'
        'eval ${status_cmd};'
        )

    def process(self, device, results, log):
        log.info('processing %s for device %s', self.name(), device.id)
        maps = list()

        """ Example output through 10.12

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
        caching:Peers:_array_index:0:address = "aaa.bbb.ccc.ddd"
        caching:Peers:_array_index:0:port = 49094
        caching:Peers:_array_index:0:details:capabilities:ur = yes
        caching:Peers:_array_index:0:details:capabilities:sc = yes
        caching:Peers:_array_index:0:details:capabilities:pc = no
        caching:Peers:_array_index:0:details:capabilities:im = no
        caching:Peers:_array_index:0:details:capabilities:ns = yes
        caching:Peers:_array_index:0:details:capabilities:query-parameters = yes  # noqa
        caching:Peers:_array_index:0:details:cache-size = 900000000000
        caching:Peers:_array_index:0:details:ac-power = yes
        caching:Peers:_array_index:0:details:is-portable = no
        caching:Peers:_array_index:0:details:local-network:_array_index:0:speed = 1000  # noqa
        caching:Peers:_array_index:0:details:local-network:_array_index:0:wired = yes  # noqa
        caching:Peers:_array_index:0:healthy = yes
        caching:Peers:_array_index:0:version = "161"
        caching:Peers:_array_index:0:friendly = yes
        caching:Peers:_array_index:0:guid = "9B9CDED4-F70C-4910-B7D4-11D1530AD34D"  # noqa
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
        service = dict()
        caches = dict()
        peers = dict()
        parents = dict()
        lines = results.splitlines()

        # Legacy output
        if not results.startswith('{'):
            output = dict(line.split(' = ') for line in lines)
            for key in output:
                if key.startswith('caching:CacheDetails:'):
                    short = key.replace(
                        'caching:CacheDetails:_array_index:',
                        ''
                        )
                    idx = int(short.split(':')[0])
                    k = short.split(':')[1]
                    v = output.get(key).replace('"', '')
                    if idx not in caches:
                        caches[idx] = dict()
                    caches[idx].update({k: v})
                elif key.startswith('caching:Peers:'):
                    short = key.replace('caching:Peers:_array_index:', '')
                    short = short.replace('details:', '')
                    if ('capabilities' not in key
                            and 'local-network' not in key):
                        idx = int(short.split(':')[0])
                        k = short.split(':')[1]
                        v = output.get(key).replace('"', '')
                        if idx not in peers:
                            peers[idx] = dict()
                        peers[idx].update({k: v})
                else:
                    k = key.split(':')[1]
                    service.update({k: output.get(key).replace('"', '')})

        # JSON output
        else:
            for line in lines:
                output = json.loads(line)
                service.update(output.get('result', dict()))

                # Mimic structure of legacy output
                keys = service.get('CacheDetails', dict()).keys()
                for idx in range(0, len(keys)):
                    value = service.get('CacheDetails', dict()).get(keys[idx])
                    caches[idx] = {
                        'MediaType': keys[idx],
                        'BytesUsed': value,
                        }
                    if len(keys) - 1 == idx:
                        break

                peer_count = 0
                for peer in service.get('Peers', dict()):
                    peers[peer_count] = peer
                    peer_count += 1
                    for attr in ('ac-power', 'cache-size', 'is-portable'):
                        if attr in peer['details']:
                            peer[attr] = peer['details'][attr]

                parents.update(service.get('Parents', dict()))

        # Caching Service
        booleans = [
            'Active',
            'AllowPersonalCaching',
            'LocalSubnetsOnly',
            'LogClientIdentity',
            'RestrictedMedia',
            ]

        for attr in booleans:
            if attr in service and type(service[attr]) is not bool:
                service[attr] = True if 'yes' == service[attr] else False

        integers = [
            #'Active',
            'CacheFree',
            'CacheLimit',
            'CacheUsed',
            'Port',
            'ReservedVolumeSpace',
            ]

        for attr in integers:
            if attr in service and type(service[attr]) is not int:
                service[attr] = int(service[attr])

        service['id'] = self.prepId('CachingService')
        service['title'] = service.get('DataPath', 'Content Caching')

        # Escape spaces in DataPath for zencommand later
        if 'DataPath' in service:
            service['DataPath'] = service['DataPath'].replace(' ', r'\ ')

        # Not listening, service likely not running
        if 'Port' in service and service.get('Port') == 0:
            del service['Port']
        log.debug('Caching Service\n%s', service)

        rm = RelationshipMap(
            relname='contentCachingService',
            modname='ZenPacks.daviswr.OSX.Server.Caching.ContentCachingService'
            )
        rm.append(ObjectMap(
            modname='ZenPacks.daviswr.OSX.Server.Caching.ContentCachingService',  # noqa
            data=service
            ))
        maps.append(rm)

        # Individual Cache components
        rm = RelationshipMap(
            compname='contentCachingService/CachingService',
            relname='contentCaches',
            modname='ZenPacks.daviswr.OSX.Server.Caching.ContentCache'
            )

        for idx in caches:
            cache = caches.get(idx)
            if 'BytesUsed' in cache:
                cache['BytesUsed'] = int(cache['BytesUsed'])
            cache['title'] = self.prepId(cache.get('MediaType', ''))
            cache['id'] = self.prepId(cache['title'])
            log.debug('Individual Cache: %s', cache)
            rm.append(ObjectMap(
                modname='ZenPacks.daviswr.OSX.Server.Caching.ContentCache',
                data=cache
                ))
        maps.append(rm)

        # Peer Server components
        rm = RelationshipMap(
            compname='contentCachingService/CachingService',
            relname='contentCachePeers',
            modname='ZenPacks.daviswr.OSX.Server.Caching.ContentCachePeer'
            )

        peer_integers = [
            'cache-size',
            'port',
            ]
        peer_booleans = [
            'ac-power',
            'friendly',
            'healthy',
            'is-portable',
            ]

        for idx in peers:
            peer = peers.get(idx)
            for attr in peer_integers:
                if attr in peer and type(peer[attr]) is not int:
                    peer[attr] = int(peer[attr])
            for attr in peer_booleans:
                if attr in peer and type(peer[attr]) is not bool:
                    peer[attr] = True if 'yes' == peer[attr] else False
            peer['title'] = peer.get('address', peer.get('guid', ''))
            id_str = 'cachepeer_{0}'.format(
                peer.get('address', peer.get('guid', ''))
                )
            peer['id'] = self.prepId(id_str)
            log.debug('Peer Caching Server: %s', peer)
            rm.append(ObjectMap(
                modname='ZenPacks.daviswr.OSX.Server.Caching.ContentCachePeer',
                data=peer
                ))
        maps.append(rm)

        return maps
