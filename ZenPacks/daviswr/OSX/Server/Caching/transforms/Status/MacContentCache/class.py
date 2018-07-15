from zenoss.protocols.protobufs.zep_pb2 import (
    SEVERITY_CLEAR,
    SEVERITY_WARNING,
    SEVERITY_ERROR,
    )

# Example: caching|caching_state|Status
if (evt.eventKey.startswith('caching|caching_')
        and evt.eventKey.endswith('|Status')):

    current = int(float(evt.current))

    name = evt.eventKey.replace('caching|caching_', '').replace('|Status', '')
    if name.endswith('Status'):
        name = name[:-6]

    state_dict = dict()
    state_dict['Registration'] = {
        -1: 'is not registered',
        1: 'is registered',
        }
    state_dict['Cache'] = {
        1: 'is OK',
        2: 'is low on space',
        }
    state_dict['Startup'] = {
        1: 'startup is OK',
        2: 'startup is pending',
        3: 'startup has failed',
        4: 'startup is not auto-enabled',
        }
    state_dict['state'] = {
        1: 'is running',
        2: 'is starting',
        3: 'is stopped',
        }
    state_dict['RegistrationError'] = {
        3: 'registration error: wireless portable is not supported',
        4: 'registration error: invalid IP range',
        5: 'registration error: public IP not in range',
        6: 'registration error: too many private addresses',
        7: 'registration error: invalid device',
        }
    state_dict['Active'] = {
        1: 'is active',
        3: 'is not active',
        }

    status = state_dict.get(name, dict()).get(
        current,
        '{0} value unknown'.format(name)
        )
    evt.summary = 'Content Cache {0}'.format(status)

    sev_dict = {
        -1: SEVERITY_ERROR,
        1: SEVERITY_CLEAR,
        2: SEVERITY_WARNING,
        3: SEVERITY_ERROR,
        4: SEVERITY_ERROR,
        5: SEVERITY_ERROR,
        6: SEVERITY_ERROR,
        7: SEVERITY_ERROR,
        }
    evt.severity = sev_dict.get(current, SEVERITY_WARNING)

    # ZPL Components look for events in /Status rather than
    # /Status/ClassName to determine up/down status
    if current != 2:
        evt.eventClass = '/Status'

    # Based on stock /Status/Perf class transform for ifOperStatus events
    if ('Active' == name or 'state' == name) and component is not None:
        bool_dict = {
            1: True,
            3: False,
            }
        if component.Active != bool_dict.get(current, False):
            @transact
            def updateDb():
                component.Active = bool_dict.get(current, False)
            updateDb()


elif 'Peers|Peers_healthy|PeerHealth' == evt.eventKey:
    current = int(float(evt.current))

    health_dict = {
        1: 'healthy',
        2: 'not healthy',
        }

    status = health_dict.get(current, 'unknown')
    evt.summary = 'Peer {0} is {1}'.format(evt.component, status)

    sev_dict = {
        1: SEVERITY_CLEAR,
        2: SEVERITY_WARNING,
        }
    evt.severity = sev_dict.get(current, SEVERITY_WARNING)

    evt.eventClass = '/Status'

    if component is not None:
        bool_dict = {
            1: True,
            2: False
            }
        if component.healthy != bool_dict.get(current, False):
            @transact
            def updateDb():
                component.healthy = bool_dict.get(current, False)
            updateDb()
