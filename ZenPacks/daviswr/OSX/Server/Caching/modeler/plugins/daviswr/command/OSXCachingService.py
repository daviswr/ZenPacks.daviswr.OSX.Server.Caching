from Products.DataCollector.plugins.CollectorPlugin import CommandPlugin
from Products.DataCollector.plugins.DataMaps import MultiArgs, RelationshipMap, ObjectMap

class OSXCachingService(CommandPlugin):
    # Command to run on monitored device.
    serveradmin = '/Applications/Server.app/Contents/ServerRoot/usr/sbin/serveradmin'
    command = 'sudo {0} settings caching; sudo {0} fullstatus caching'.format(serveradmin)

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
                k = 'cacheDetails' + short.split(':')[1]
                v = output.get(key).replace('"', '')
                if not caches.has_key(idx):
                  caches[idx] = dict()
                caches[idx].update({k: v})
            else:
                service.update({key.replace(':', ''): output.get(key).replace('"', '')})

        # Caching Service
        if service.has_key('cachingstate'):
            service['cachingState'] = service.get('cachingstate')
            del service['cachingstate']

        for boolean in ['cachingActive', 'cachingRestrictedMedia', 'cachingLocalSubnetsOnly']:
            if service.has_key(boolean):
               service[boolean] = True if ('yes' == service[boolean]) else False

        for numeric in ['cachingCacheLimit', 'cachingReservedVolumeSpace', \
            'cachingCacheUsed', 'cachingCacheFree', 'cachingPort']:
            if service.has_key('numeric'):
                service[numeric] = int(service[numeric])

        service['id'] = self.prepId('CachingService')
        service['title'] = service.get('cachingServerRoot',
            service.get('cachingDataPath', 'Caching Service'))
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
            relname='caches',
            modname='ZenPacks.daviswr.OSX.Server.Caching.Cache'
            )

        for idx in caches:
            cache = caches.get(idx)
            if cache.has_key('cacheDetailsBytesUsed'):
                cache['cacheDetailsBytesUsed'] = int(cache['cacheDetailsBytesUsed'])
            lang = cache.get('cacheDetailsLanguage', '')
            suffix = ' ({})'.format(lang) if (len(lang) > 0) else ''
            cache['id'] = self.prepId(cache.get('cacheDetailsMediaType',
                'Cache {}'.format(str(idx))) + '-' + lang)
            cache['title'] = cache.get('cacheDetailsLocalizedType',
                cache.get('cacheDetailsMediaType', 'Cache {}'.format(str(idx))) + 'suffix')
            log.debug('Individual Cache: %s', cache)
            rm.append(ObjectMap(
                modname='ZenPacks.daviswr.OSX.Server.Caching.Cache',
                data=cache
                ))
        maps.append(rm)

        return maps
