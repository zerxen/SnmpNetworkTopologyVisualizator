import json
from helpers import *
import pprint
from pyconfig import *
from random import randint
import time
from datetime import datetime


if __name__ == "__main__":

    ##############
    # ENTRY DATA #
    ##############
    deviceid = "VSR1000"
    INDEX = 47
    ifDescr = "GigabitEthernet0/0"
    ifHCInOctets = randint(0, 1000)
    ifHCOutOctets = randint(0, 1000)
    ifSpeed = 1000000000

    log("ifHCInOctets: "+ str(ifHCInOctets))
    log("ifHCOutOctets: " + str(ifHCOutOctets))

    try:
        with open('html/data/interface_stats.json') as json_file:
            interface_stats = json.load(json_file)
    except FileNotFoundError:
        log("File doesn't exists, creating...")
        interface_stats = dict()

    #
    # READ IS DONE, NOW WE CHECK
    #
    #print(json.dumps(interface_stats, indent=4))

    #
    # EXTEND
    #

    now = datetime.now()
    print("Now: " + str(now))
    # print("Printable: " + str(now.strftime('%Y-%m-%d %H:%M:%S')))
    timestamp = int(datetime.timestamp(now))
    print("Timestamp: " + str(timestamp))
    # REVERSE IS
    #time.sleep(1)
    #print("Timestamp: " + str(int(datetime.timestamp(datetime.now()))))
    #time.sleep(10)
    #print("Timestamp: " + str(int(datetime.timestamp(datetime.now()))))



    #// Get device specific data, or create empty set
    if deviceid not in interface_stats:
        log("first time log for this device ID: " + deviceid)
        device_interfaces_stats = {
            "interfaces": [
                {
                    "index": INDEX,
                    "ifDescr": ifDescr,
                    "last_timestamp":timestamp,
                    "last_ifHCInOctets":ifHCInOctets,
                    "last_ifHCOutOctets":ifHCOutOctets,
                    "stats":[

                    ]
                }

            ]
        }

    else:
        log("device ID: " + deviceid + " exists in the source JSON")
        # OK this is not the first time this device is having stats!
        device_interfaces_stats = interface_stats[deviceid]

        # Lets locate the correct interface on this device
        interface_found = False
        for interface in device_interfaces_stats['interfaces']:
            if interface['index'] == INDEX:
                interface_found = True
                device_interface_stats = interface
                break

        # if not found, lets create a new entry
        if not interface_found:
            device_interface_stats = {
                    "index": INDEX,
                    "ifDescr": ifDescr,
                    "last_timestamp": timestamp,
                    "last_ifHCInOctets": ifHCInOctets,
                    "last_ifHCOutOctets": ifHCOutOctets,
                    "stats": [

                    ]
                }
            device_interfaces_stats['interfaces'].append(device_interface_stats)

        # Here we have a found device and found non-empty interface stats
        else:

            # OK, lets get the last timestamp and values to get current bandwith
            last_ifHCInOctets = device_interface_stats['last_ifHCInOctets']
            last_ifHCOutOctets = device_interface_stats['last_ifHCOutOctets']
            last_timestamp = int(device_interface_stats["last_timestamp"])

            # IF NEW COUNTERS ARE SMALLER THAN PREVIOUS, PROBABLY A COUNTER WRAP AND WE SKIP
            if ifHCInOctets > last_ifHCInOctets and ifHCOutOctets > last_ifHCOutOctets:

                delta_time = timestamp - last_timestamp
                delta_ifHCInOctets = ifHCInOctets - last_ifHCInOctets
                delta_ifHCOutOctets = ifHCOutOctets - last_ifHCOutOctets

                log("delta_ifHCInOctets: " + str(delta_ifHCInOctets))
                log("delta_ifHCOutOctets: " + str(delta_ifHCOutOctets))
                log("delta_time: " + str(delta_time))

                # This means our speed on In was :
                InSpeed = int(delta_ifHCInOctets * 8 * 100 / delta_time)
                OutSpeed = int(delta_ifHCOutOctets * 8 * 100 / delta_time)

                # Utilization
                utilization = int(max(InSpeed,OutSpeed) / ifSpeed)
                device_interface_stats['utilization'] = utilization

                log("InSpeed: "+ str(InSpeed))
                log("OutSpeed: " + str(OutSpeed))
                log("Utilization: " + str(utilization))

                # add to graph the stats value
                device_interface_stats['stats'].append(
                    {
                        "time": now.strftime('%Y-%m-%d %H:%M:%S'),
                        "InSpeed": InSpeed,
                        "OutSpeed": OutSpeed
                    }
                )


            else:
                log("Skipped as counters probably wrapped")

            # update the "last" values
            device_interface_stats['last_ifHCInOctets'] = ifHCInOctets
            device_interface_stats['last_ifHCOutOctets'] = ifHCOutOctets
            device_interface_stats["last_timestamp"] = timestamp


    #
    # READ IS DONE, NOW WE CHECK
    #
    print(json.dumps(interface_stats, indent=4))

    interface_stats[deviceid] = device_interfaces_stats
    with open('html/data/interface_stats.json', 'w') as outfile:
        json.dump(interface_stats, outfile, sort_keys=True, indent=4)
        log("JSON printed into graph.json")