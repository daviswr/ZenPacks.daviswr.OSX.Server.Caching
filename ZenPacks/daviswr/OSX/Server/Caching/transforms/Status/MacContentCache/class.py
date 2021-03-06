from zenoss.protocols.protobufs.zep_pb2 import (
    SEVERITY_CLEAR,
    SEVERITY_WARNING,
    SEVERITY_ERROR
    )

current = int(float(evt.current))

# Example: caching|caching_state|Status
if (evt.eventKey.startswith('caching|caching_')
        and evt.eventKey.endswith('|Status')):

    name = evt.eventKey.replace('caching|caching_', '').replace('|Status', '')
    if name.endswith('Status'):
        name = name[:-6]

    state_dict = dict()
    state_dict['Registration'] = {
        -1: 'is not registered',
        0: 'is attempting registration',
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
        8: 'registration error: not activated',
        }
    state_dict['Active'] = {
        0: 'is not active',
        1: 'is active',
        }
    state_dict['DiskExceededCustom'] = {
        1: 'size is within available volume capacity',
        2: 'size exceeds available volume capacity',
        }

    status = state_dict.get(name, dict()).get(
        current,
        '{0} value unknown'.format(name)
        )
    evt.summary = 'Content Cache {0}'.format(status)

    sev_dict = {
        -1: SEVERITY_ERROR,
        0: SEVERITY_WARNING,
        1: SEVERITY_CLEAR,
        2: SEVERITY_WARNING,
        3: SEVERITY_ERROR,
        4: SEVERITY_ERROR,
        5: SEVERITY_ERROR,
        6: SEVERITY_ERROR,
        7: SEVERITY_ERROR,
        8: SEVERITY_ERROR,
        }
    evt.severity = sev_dict.get(current, SEVERITY_WARNING)

    # ZPL Components look for events in /Status rather than
    # /Status/ClassName to determine up/down status
    if current != 2 and name != 'DiskExceededCustom':
        evt.eventClass = '/Status'

    if (name in ['Active', 'state']
            and component
            and hasattr(component, 'Active')):
        bool_dict = {
            0: False,
            1: True,
            3: False,
            }
        if component.Active != bool_dict.get(current, False):
            @transact
            def updateDb():
                component.Active = bool_dict.get(current, False)
            updateDb()

elif 'Peers|Peers_healthy|PeerHealth' == evt.eventKey:
    health_dict = {
        0: 'not healthy',
        1: 'healthy',
        }

    status = health_dict.get(current, 'unknown')
    evt.summary = 'Peer {0} is {1}'.format(evt.component, status)

    sev_dict = {
        0: SEVERITY_WARNING,
        1: SEVERITY_CLEAR,
        }
    evt.severity = sev_dict.get(current, SEVERITY_WARNING)

    evt.eventClass = '/Status'

    if component and hasattr(component, 'healthy'):
        bool_dict = {
            0: False,
            1: True,
            }
        if component.healthy != bool_dict.get(current, False):
            @transact
            def updateDb():
                component.healthy = bool_dict.get(current, False)
            updateDb()
