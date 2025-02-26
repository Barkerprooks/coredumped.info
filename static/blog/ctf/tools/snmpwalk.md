# SNMPWalk - SNMP Enumeration
An enumeration tool for SNMP networked devices

## Quick start
enumerate the hierarchy for a `SNMP` domain. If you don't know the community string, common ones are `public` and `private`. Start on the lowest supported protocol version and work your way up. 

You can dump public records like this. Using version `2c` means authentication is not 
required    

    snmpwalk -v 2c -c public $target_ip
