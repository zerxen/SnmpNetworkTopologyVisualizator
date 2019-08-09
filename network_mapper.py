import pprint
import argparse
import textwrap
import json
import configparser
import quicksnmp
from pysnmp import hlapi
import code
import helpers
from helpers import log
from Classes.TopologyModel import NetworkTopology
from pyconfig import *
import time


def main_with_args(args):
    log("############")
    log("# Starting #")
    log("############")
    '''
    Lets create a data model of the topology from the above information
    '''
    topology_model = NetworkTopology()

    '''
    Lets go via devices and get data
    '''
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.sections()
    if 'DEVICES' not in config or 'DEFAULT' not in config:
        log('We failed to load the configuration file, and sections from it, exiting')
        exit(1)

    for device in json.loads(config['DEVICES']['devices']):
        device = device.replace('\n', '')
        print("")
        print("############################################")
        print(f'Testing access to {device:15} ...', end=" ")
        log("Testing access to " + device)

        '''
        Try getting first the device hostname to check if SNMP works
        '''
        try:
            sSNMPHostname = quicksnmp.get(device, sysName_named_oid,
                                          hlapi.CommunityData(config['DEFAULT']['SnmpCommunityString']))
            log(' = '.join([x.prettyPrint() for x in sSNMPHostname]))
            log(" This is how to get to numeric OID: " + str(tuple(sSNMPHostname[0][0])))
            log(" This is how to get data only: " + str(sSNMPHostname[0][1]))
        except RuntimeError as e:
            log("Runtime Error: " + str(e))
            continue
        except (ValueError, TypeError):
            log("Error " + str(TypeError))
            continue

        log("# Connection worked, will retrieve data next")

        '''
        INTERFACES TABLE GET
        '''
        try:
            log("INTERFACES TABLE: ")
            rawInterfacesTable = quicksnmp.get_table(device, interfaces_table_named_oid,
                                                     hlapi.CommunityData(config['DEFAULT']['SnmpCommunityString']))
            for row in rawInterfacesTable:
                for item in row:
                    log(' = '.join([x.prettyPrint() for x in item]))
                log('')

        except RuntimeError as e:
            log("Runtime Error: " + str(e))
            continue
        except (ValueError, TypeError):
            log("Error " + str(TypeError))
            continue

        '''
        LLDP TABLE GET
        '''
        try:
            log("LLDP TABLE: ")
            log("############")
            rawTable = quicksnmp.get_table(device, lldp_table_named_oid,
                                           hlapi.CommunityData(config['DEFAULT']['SnmpCommunityString']))
            for row in rawTable:
                for item in row:
                    log(' = '.join([x.prettyPrint() for x in item]))
                log('')

        except RuntimeError as e:
            log("Runtime Error: " + str(e))
            continue
        except (ValueError, TypeError):
            log("Error " + str(TypeError))
            continue

        ''' 
        Populate data model with this device data
        '''
        topology_model.addDevice(str(sSNMPHostname[0][1]))

        for row in rawInterfacesTable:
            # index number from OID
            oid = tuple(row[0][0])
            log('INDEX: ' + str(oid[-1]))
            # ifDescr
            log('ifDescr: ' + str(row[0][1]))
            # ifType
            log('ifType: ' + str(row[1][1]))
            # ifMtu
            log('ifMtu: ' + str(row[2][1]))
            # ifSpeed
            log('ifSpeed: ' + str(row[3][1]))
            # ifPhysAddress
            log('ifPhysAddress: ' + str(row[4][1].prettyPrint()))
            # ifAdminStatus
            log('ifAdminStatus: ' + str(row[5][1]))
            # ifOperStatus
            log('ifOperStatus: ' + str(row[6][1]))
            # ifHCInOctets
            log('ifHCInOctets: ' + str(row[7][1]))
            # ifHCOutOctets
            log('ifHCOutOctets: ' + str(row[8][1]))
            # ifHighSpeed
            log('ifHighSpeed: ' + str(row[9][1]))
            log("")

            topology_model.addDeviceInterface(str(sSNMPHostname[0][1]),  # deviceid
                                              oid[-1],  # INDEX
                                              str(row[0][1]),  # ifDescr
                                              str(row[1][1]),  # ifType
                                              str(row[2][1]),  # ifMtu
                                              str(row[3][1]),  # ifSpeed
                                              str(row[4][1].prettyPrint()),  # ifPhysAddress
                                              str(row[5][1]),  # ifAdminStats
                                              str(row[6][1]))  # ifOperStatus

            topology_model.addInterfaceStats(str(sSNMPHostname[0][1]),  # deviceid
                                             oid[-1],  # INDEX
                                             str(row[0][1]),  # ifDescr
                                             str(row[1][1]),  # ifType
                                             str(row[6][1]),  # ifOperStatus
                                             str(row[7][1]),  # ifHCInOctets
                                             str(row[8][1]),  # ifHCOutOctets
                                             str(row[9][1]))  # ifHighSpeed

        log('links from LLDP')
        for row in rawTable:
            # lldpRemSysName
            log('lldpRemSysName: ' + str(row[0][1]))
            # lldpRemSysDesc
            log('lldpRemSysDesc: ' + str(row[1][1]))
            # lldpRemPortId
            log('lldpRemPortId: ' + str(row[2][1]))
            # lldpRemPortDesc
            log('lldpRemPortDesc: ' + str(row[3][1]))

            # Add to neighborships
            oid = tuple(row[0][0])
            local_in_index = oid[-2]
            # Get interface name via LLDP local int table
            local_interface_name = quicksnmp.get(device, [('LLDP-MIB', 'lldpLocPortId', local_in_index)],
                                                 hlapi.CommunityData(config['DEFAULT']['SnmpCommunityString']))

            # Repairing H3Cs bad indexes by searching for index via name
            local_in_index = topology_model.getDeviceInterfaceIndex(str(sSNMPHostname[0][1]), str(local_interface_name[0][1]))

            log("Local_interface_name: " + str(local_interface_name[0][1]))
            log(' = '.join([x.prettyPrint() for x in local_interface_name]))

            # Add to links
            topology_model.addLink(str(sSNMPHostname[0][1]),  # node_a
                                   str(row[0][1]),  # node_b
                                   topology_model.getLinkSpeedFromName(str(row[2][1])),
                                   local_in_index,  # a_local_int_index
                                   str(local_interface_name[0][1]),  # a_local_int_name
                                   str(row[2][1])  # lldpRemPortId
                                   )

            log("Localintindex : " + str(local_in_index))
            topology_model.addNeighborships(str(sSNMPHostname[0][1]),
                                            local_in_index,
                                            str(local_interface_name[0][1]),
                                            str(row[0][1]),
                                            str(row[2][1]))

    '''
    The model should be populated now, lets dump the JSONs
    '''
    topology_model.dumpToJSON()
    del topology_model

    return 0;


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=textwrap.dedent('''\
             -----------------------------
                                         ..   ..  ..  .... ..                               
                                    ,7MMMMMMMMMMMMMMMMMMMMMMMMMN7,                          
                               IMMMMS...MMMMMMMMMMMMMMMMM+..,,,,,,,MMMS.                    
                          ..+MMMMMMMM,,,,,,,MMMMMMMMMMMMMM:,,,,: ..,MMMMMM.                 
                          MMMMMMMMMMMMMMM.,,,,..,,MMMM,,,,,,:MMMMMMMMMMMMMMM                
                         MMMMMMMMMMMMMMMNMMMMMMMMMMMMMM MMMMMMMMMMMMMMMMMMMMM               
                         NMMMMMMMMMMMMMMMMMMM8,.MMMMMMMMMMMMMMMMMMMMMMMMMMMMZ               
             M           NMMMMMMMMMMMMMMM8,,,,,,MMMM,,,,,,,,MMMMMMMMMMMMMMZM            M  
             SM          NMMMMMMMM,.....,,,,MMMMMMMMMMMMMMM.,,,,,7MMMMMMMMMMM           M,  
             .MM.        NMMMMMMZMMI,,,,,,,.,MMMMMMMMMMMMMMMMM8.,. MMZMMMMMMM         .MM   
              :MMM       NMMMMMMMMMMMMMZMMMMMMMMMMMMMMMMMMMMMM7MMMMMMMMMMMMMM        MM    
               MMMM.     NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM       MMMM    
                MMMMZ.   NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM     .MMMM.    
                 MMMMM  .NMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM   .+MMMM      
                 .MMMMM  .MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.  .NMMMM.      
                   MMMMMM  :MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.   MMMMM        
                    MMMMMM+   ~MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.   .MMMMMM         
                     MMMMMMM.      MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM.       :MMMMMM          
                       MMMMMMN        . .. . ,NMNNNNNNNM.,. .. .         :MMMMMMM.          
                        MMMMMMMN                                       ZMMMMMMM.            
                         IMMMMMMMM.                                  OMMMMMMMZ              
                          .MMMMMMMMM                               MMMMMMMMM.               
                             MMMMMMMMM                          .MMMMMMMMM.                 
                               MMMMM.MMM                      ,MMMMMMMMM.                   
                                ~MMMMM.MMM:.                NMM8 MMMMM                      
                                  ,MMMMO.MMMM.           +MMM. MMMMM                        
                         .          .MMMMM..MMMN.   ..MMMM. IMMMMM                          
                        .MMMM          ~MMMMM .MMMM...M.. MMMMM          . .                
                          MMM.            MMMMMM..MMMMM  .MM+..         =MMMM               
                          .7MM         +MMM .MMMMMM. ~MMMMMI           .MMM                 
                 .  .       MMM ~MMMMMMMMM.. .=.+NMMMMM  MMMMMMM. .   MMM                  
                 MMMMMMMMM+.MMMM .+I .  MMMMMMMM ..MMMMMMM  SMMMMMM:.MMM                   
                 MMMM MMMMMMM  MMM  MMMMMMM  .         DMMMMMM    SMMMM ,MMMMMM.MMM        
                 .MMM. ..     .MMM  ..                       .,MMM. MMM MMMMMMMMMMM.       
                     M         MMM .                                MM,       ..MMMM        
                               .MMMM .Z.                           MMM         MM           
                                  MMMMMM                     MMMMMMMM                       
                                                              OMMM

             (c) Peter Havrila - networkgeekstuff.com
             phavrila@gmail.com

            '''),
        prog='network_mapper',
        epilog="2019 (c) Peter Havrila",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')
    parser.add_argument("-R", "--REPEAT", default=0, type=int,
                        help="If provided, program will re-run itself every X seconds")
    parser.set_defaults(func=main_with_args)

    # Binding parsers to arges
    args = parser.parse_args()
    if args.REPEAT == 0:
        return_code = args.func(args)
    else:
        while (True):
            return_code = args.func(args)
            time.sleep(args.REPEAT)

    print("return code:" + str(return_code))
    exit(return_code)
