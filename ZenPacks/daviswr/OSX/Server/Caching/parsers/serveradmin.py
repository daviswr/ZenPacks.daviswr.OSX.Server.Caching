from Products.ZenRRD.CommandParser \
    import CommandParser
from Products.ZenUtils.Utils \
    import prepId


class serveradmin(CommandParser):

    def processResults(self, cmd, result):
        components = dict()

        lines = cmd.result.output.splitlines()
        output = dict(line.split(' = ') for line in lines)
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
        component_id = prepId('CachingService')
        if component_id not in components:
            components[component_id] = dict()

        datapoints = [
            'CacheFree',
            'CacheUsed',
            'PackageCountCustom',
            'PersonalCacheFree',
            'PersonalCacheUsed',
            'RegistrationStatus',
            'TotalBytesDropped',
            'TotalBytesImported',
            'TotalBytesReturned',
            'TotalBytesStored',
            'TotalBytesStoredFromOrigin',
            'TotalBytesStoredFromPeers',
            ]

        for measure in datapoints:
            if measure in service:
                value = int(service[measure])
                if 'Free' in measure and value < 0:
                    value = 0
                components[component_id][measure] = value

        # Transform state strings into integers
        # so they can be monitored by a performance template
        attr_map = dict()
        attr_map['CacheStatus'] = {
            'OK': 1,
            'LOWSPACE': 2,
            }

        attr_map['StartupStatus'] = {
            'OK': 1,
            'PENDING': 2,
            'FAILED': 3,
            'NO_AUTO_ENABLE': 4,
            }

        attr_map['state'] = {
            'RUNNING': 1,
            'STARTING': 2,
            'STOPPED': 3,
            }

        attr_map['RegistrationError'] = {
            'WIRELESS_PORTABLE_NOT_SUPPORTED': 3,
            'INVALID_IP_RANGE': 4,
            'PUBLIC_IP_NOT_IN_RANGE': 5,
            'TOO_MANY_PRIVATE_ADDRESSES': 6,
            'INVALID_DEVICE': 7,
            }

        attr_map['Active'] = {
            'yes': 1,
            'no': 3,
            }

        for attr in attr_map:
            if attr in service:
                value = attr_map[attr].get(service[attr], 0)
                components[component_id][attr] = value

        if 'RegistrationError' not in components[component_id]:
            components[component_id]['RegistrationError'] = 1

        # Individual cache
        for idx in caches:
            cache = caches.get(idx)
            alt_id = 'Cache {0}_{1}'.format(idx, cache.get('Language', ''))
            component_id = prepId(cache.get('MediaType', alt_id))
            if component_id not in components:
                components[component_id] = dict()
            value = int(cache.get('BytesUsed'))
            components[component_id]['BytesUsed'] = value

        # Peer server
        health_map = {
            'yes': 1,
            'no': 2,
            }

        for idx in peers:
            peer = peers.get(idx)
            id_str = '{0}:{1}'.format(
                peer.get('address', ''),
                str(peer.get('port', ''))
                )
            component_id = prepId(id_str)
            if component_id not in components:
                components[component_id] = dict()
            value = health_map.get(peer.get('healthy'), 0)
            components[component_id]['healthy'] = value

        for point in cmd.points:
            if point.component in components:
                values = components[point.component]
                if point.id in values:
                    result.values.append((point, values[point.id]))
