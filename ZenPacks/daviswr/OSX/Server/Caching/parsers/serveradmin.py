import json
from Products.ZenRRD.CommandParser \
    import CommandParser
from Products.ZenUtils.Utils \
    import prepId


class serveradmin(CommandParser):

    def processResults(self, cmd, result):
        components = dict()
        service = dict()
        caches = dict()
        peers = dict()
        parents = dict()
        lines = cmd.result.output.splitlines()

        # Legacy output
        if not cmd.result.output.startswith('{'):
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
                if 'PackageCountCustom' in output:
                    service.update(output)

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
                    for attr in ('ac-power', 'is-portable'):
                        if attr in peer['details']:
                            peer[attr] = peer['details'][attr]

                parents.update(service.get('Parents', dict()))
            # Generate missing datapoint
            total_returned = service.get('TotalBytesReturnedToClients', 0)
            total_returned += service.get('TotalBytesReturnedToChildren', 0)
            total_returned += service.get('TotalBytesReturnedToPeers', 0)
            service['TotalBytesReturned'] = total_returned

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
            'TotalBytesReturnedToChildren',
            'TotalBytesReturnedToClients',
            'TotalBytesReturnedToPeers',
            'TotalBytesStored',
            'TotalBytesStoredFromOrigin',
            'TotalBytesStoredFromParents',
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
            'no': 0,
            'yes': 1,
            False: 0,
            True: 1,
            }

        for attr in attr_map:
            if attr in service:
                value = attr_map[attr].get(service[attr], -2)
                components[component_id][attr] = value

        if 'RegistrationError' not in components[component_id]:
            components[component_id]['RegistrationError'] = 1

        # Individual cache
        for idx in caches:
            cache = caches.get(idx)
            component_id = prepId(cache.get('MediaType'))
            if component_id not in components:
                components[component_id] = dict()
            value = int(cache.get('BytesUsed'))
            components[component_id]['BytesUsed'] = value

        # Peer server
        health_map = {
            'no': 0,
            'yes': 1,
            False: 0,
            True: 1,
            }

        for idx in peers:
            peer = peers.get(idx)
            id_str = 'peercache_{0}'.format(
                peer.get('address', peer.get('guid', ''))
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
