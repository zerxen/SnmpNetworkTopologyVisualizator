from pysnmp import hlapi
import code
import itertools

# SNMPv3 alternative
'''
hlapi.UsmUserData('testuser', authKey='authenticationkey', privKey='encryptionkey', authProtocol=hlapi.usmHMACSHAAuthProtocol, privProtocol=hlapi.usmAesCfb128Protocol)
'''


def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types_from_named_oid(oids)
    )
    return fetch(handler)


def get_next(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.nextCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types_from_named_oid(oids)
    )
    return fetch(handler)


def get_bulk(target, oids, credentials, count, start_from=0, port=161,
             engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.bulkCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        start_from, count,
        *construct_object_types_from_named_oid(oids),
        lexicographicMode=True
    )
    return fetch(handler)


def get_bulk_auto(target, oids, credentials, count_oid, start_from=0, port=161,
                  engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    count = get(target, count_oid, credentials, port, engine, context)[count_oid][0]
    return get_bulk(target, oids, credentials, count, start_from, port, engine, context)


def get_table(target, oids, credentials, start_from=0, port=161,
              engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.nextCmd(
        engine,
        credentials,
        hlapi.UdpTransportTarget((target, port)),
        context,
        *construct_object_types_from_named_oid(oids),
        lexicographicMode=False
    )
    return cut_array_to_table(fetch(handler),len(oids))


def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid).addMibSource('.')))
    return object_types


def construct_object_types_from_named_oid(list_of_oid_name_tuplets):
    object_types = []
    for oid in list_of_oid_name_tuplets:
        addr = []
        for x in oid:
            addr.append(x)
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(*addr).addMibSource('.')))
    return object_types

'''
Example I have 14 items and I need to cut them to rows of 7 items in each, i use the data array and parameter 7
'''
def cut_array_to_table(data,collumns):
    result = []
    row = []
    collumn_index = 0
    for x in data:
        if collumn_index == 0:
            row.append(x)
            collumn_index = 1
        elif collumn_index < collumns:
            collumn_index = collumn_index + 1
            row.append(x)
            if collumn_index == collumns:
                result.append(row)
        else:
            collumn_index = 1
            row = [x] #starts new row

    return result



def fetch(handler):
    result = []

    for (errorIndication,
         errorStatus,
         errorIndex,
         varBinds) in handler:

        if errorIndication:
            print(errorIndication)
            raise RuntimeError('Got SNMP error: {0}'.format(errorIndication))
        elif errorStatus:
            print('%s at %s' % (errorStatus.prettyPrint(),
                                errorIndex and varBinds[int(errorIndex) - 1][0] or '?'))
            raise RuntimeError('Got SNMP error: {0}'.format(errorStatus))
        else:
            for varBind in varBinds:
                result.append(varBind)

    print("DEBUG: len of result from fetch() " + str(len(result)) )
    return result


def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value
