from Products.DataCollector.plugins.CollectorPlugin \
    import CommandPlugin
from Products.DataCollector.plugins.DataMaps \
    import MultiArgs, RelationshipMap, ObjectMap


class OSXCachingService(CommandPlugin):
    # Command to run on monitored device.
    serveradmin = '/Applications/Server.app/Contents/ServerRoot/' \
                  'usr/sbin/serveradmin'
    command = 'sudo {0} settings caching; ' \
              'sudo {0} fullstatus caching'.format(serveradmin)

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
        output = dict(line.split(' = ') for line in results.splitlines())
        service = dict()
        caches = dict()
        peers = dict()
        for key in output:
            if key.startswith('caching:CacheDetails:'):
                short = key.replace('caching:CacheDetails:_array_index:', '')
                idx = int(short.split(':')[0])
                k = short.split(':')[1]
                v = output.get(key).replace('"', '')
                if idx not in caches:
                    caches[idx] = dict()
                caches[idx].update({k: v})
            elif key.startswith('caching:Peers:'):
                short = key.replace('caching:Peers:_array_index:', '')
                short = short.replace('details:', '')
                if 'capabilities' not in key and 'local-network' not in key:
                    idx = int(short.split(':')[0])
                    k = short.split(':')[1]
                    v = output.get(key).replace('"', '')
                    if idx not in peers:
                        peers[idx] = dict()
                    peers[idx].update({k: v})
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
        service['title'] = service.get(
            'ServerRoot',
            service.get('DataPath', 'Caching Service')
            )
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
            suffix = ' ({0})'.format(lang) if (len(lang) > 0) else ''
            alt_id = 'Cache {0}_{1}'.format(idx, cache.get('Language', ''))
            cache['id'] = self.prepId(cache.get('MediaType', alt_id))
            cache['title'] = cache.get('LocalizedType', cache.get(
                'MediaType',
                'Cache {0}'.format(idx)
                ) + suffix)
            log.debug('Individual Cache: %s', cache)
            rm.append(ObjectMap(
                modname='ZenPacks.daviswr.OSX.Server.Caching.Cache',
                data=cache
                ))
        maps.append(rm)

        # Peer Server components
        rm = RelationshipMap(
            compname='cachingService/CachingService',
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
                if attr in peer:
                    peer[attr] = int(peer[attr])
            for attr in peer_booleans:
                if attr in peer:
                    peer[attr] = True if 'yes' == peer[attr] else False
            id_str = '{0}:{1}'.format(
                peer.get('address', ''),
                str(peer.get('port', ''))
                )
            peer['title'] = id_str
            peer['id'] = self.prepId(peer['title'])
            log.debug('Peer Caching Server: %s', peer)
            rm.append(ObjectMap(
                modname='ZenPacks.daviswr.OSX.Server.Caching.ContentCachePeer',
                data=peer
                ))
        maps.append(rm)

        return maps