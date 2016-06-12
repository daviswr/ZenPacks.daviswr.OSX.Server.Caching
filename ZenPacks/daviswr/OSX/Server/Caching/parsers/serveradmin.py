from Products.ZenRRD.CommandParser import CommandParser
from Products.ZenUtils.Utils import prepId

class caching(CommandParser):

    def processResults(self, cmd, result):
        components = dict()

        output = dict(line.split(' = ') for line in cmd.result.output.splitlines())
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
        component_id = prepId('CachingService')
            if component_id not in components:
                components[component_id] = dict()

        datapoints = [
            'CacheFree',
            'CacheUsed',
            'RegistrationStatus',
            'TotalBytesDropped',
            'TotalBytesImported',
            'TotalBytesReturned',
            'TotalBytesStored',
            'TotalBytesStoredFromOrigin',
            'TotalBytesStoredFromPeers',
             ]

        for measure in datapoints:
            value = int(service.get(measure)
            components[component_id][measure] = value

        # Individual cache
        for idx in caches:
            cache = caches.get(idx)
            component_id = prepId(cache.get('MediaType',
                'Cache {}'.format(str(idx))) \
                + '-' + cache.get('Language', ''))
            if component_id not in components:
                components[component_id] = dict()
            value = int(cache.get('BytesUsed'))
            components[component_id]['BytesUsed'] = value

        for point in cmd.points:
            if point.component in components:
                values = components[point.component]
                if point.id in values:
                    result.values.append((point, values[point.id]))
            
