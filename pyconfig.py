# TABLE ROW DEFINITIONS
sysName_named_oid = [('SNMPv2-MIB', 'sysName', 0)]

interfaces_table_named_oid = [
    ('IF-MIB', 'ifDescr'),
    ('IF-MIB', 'ifType'),
    ('IF-MIB', 'ifMtu'),
    ('IF-MIB', 'ifSpeed'),
    ('IF-MIB', 'ifPhysAddress'),
    ('IF-MIB', 'ifAdminStatus'),
    ('IF-MIB', 'ifOperStatus'),
    ('IF-MIB', 'ifHCInOctets'),
    ('IF-MIB', 'ifHCOutOctets'),
    ('IF-MIB', 'ifHighSpeed')
]

lldp_table_named_oid = [
    ('LLDP-MIB', 'lldpRemSysName'),
    ('LLDP-MIB', 'lldpRemSysDesc'),
    ('LLDP-MIB', 'lldpRemPortId'),
    ('LLDP-MIB', 'lldpRemPortDesc')
]

lldp_local_port_name = [('LLDP-MIB', 'lldpLocPortId', 0)]

#######
#STATS
#######
MAX_STATS_RECORDS = 2016

#########################################################
# REGULAR EXPLRESSIONS FOR MATCHING PORT NAMES TO SPEEDS
# NOTE: This is used in visuzation later to color lines
#########################################################
LINK_SPEEDS = [("^TwentyGigE*", "20"),
               ("^FortyGig*", "40"),
               ("^Ten-GigabitEthernet*", "10"),
               ("^GigabitEthernet*", "1")]

#########################################################
# REGULAR EXPLRESSIONS FOR MATCHING DEVICES HIERARHY
# E.g. Access layer switches have "AC" in their name
# or aggregation layer devices have "AG" in their names
#########################################################
NODE_HIERARCHY = [
                  ('^[a-zA-Z]{5}L2.*', "4", "L2.png"),
                  ('^[a-zA-Z]{5}L3.*', "5", "L3.png"),
                  ('^[a-zA-Z]{5}DS.*', "3", "DS.png"),
                  ('^[a-zA-Z]{5}AC.*', "2", "AC.png")
                  ]

IGNORED_IFTYPES = [ "l3ipvlan", "softwareLoopback", "other"]