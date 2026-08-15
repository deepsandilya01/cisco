import csv

cases = [
    # 1. VLAN misconfiguration
    {
        "case_id": "CASE-001",
        "symptom": "PC1 cannot ping PC2 in the same subnet",
        "topology_note": "PC1 on Switch1 port Fa0/1, PC2 on Switch1 port Fa0/2",
        "concept_tag": "VLAN",
        "severity": "Medium",
        "show_outputs": "Switch1#show vlan brief\n\nVLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    Fa0/1, Fa0/3, Fa0/4\n10   Sales                            active    Fa0/2\n",
        "expected_fault": "Ports are in different VLANs (Fa0/1 in VLAN 1, Fa0/2 in VLAN 10)",
        "osi_layer": "Layer 2"
    },
    {
        "case_id": "CASE-002",
        "symptom": "User complains of no network access",
        "topology_note": "User PC connected to Switch2 Gi0/1",
        "concept_tag": "VLAN",
        "severity": "Low",
        "show_outputs": "Switch2#show vlan brief\n\nVLAN Name                             Status    Ports\n---- -------------------------------- --------- -------------------------------\n1    default                          active    Fa0/1\n20   Engineering                      active    \n",
        "expected_fault": "Port Gi0/1 is not assigned to any active VLAN or is missing",
        "osi_layer": "Layer 2"
    },
    # 2. Default gateway mismatch
    {
        "case_id": "CASE-003",
        "symptom": "Host cannot reach the internet but can ping local servers",
        "topology_note": "Host IP 192.168.1.50/24, Router IP 192.168.1.1",
        "concept_tag": "Gateway",
        "severity": "High",
        "show_outputs": "Host>ipconfig\n\nIPv4 Address. . . . . . . . . . . : 192.168.1.50\nSubnet Mask . . . . . . . . . . . : 255.255.255.0\nDefault Gateway . . . . . . . . . : 192.168.1.254\n",
        "expected_fault": "Default gateway on host is configured as 192.168.1.254 instead of 192.168.1.1",
        "osi_layer": "Layer 3"
    },
    {
        "case_id": "CASE-004",
        "symptom": "Server cannot respond to remote clients",
        "topology_note": "Server IP 10.0.0.10/24, Gateway should be 10.0.0.1",
        "concept_tag": "Gateway",
        "severity": "Critical",
        "show_outputs": "Server>ipconfig\n\nIPv4 Address. . . . . . . . . . . : 10.0.0.10\nSubnet Mask . . . . . . . . . . . : 255.255.255.0\nDefault Gateway . . . . . . . . . : 0.0.0.0\n",
        "expected_fault": "Default gateway is missing (0.0.0.0)",
        "osi_layer": "Layer 3"
    },
    # 3. DHCP failure
    {
        "case_id": "CASE-005",
        "symptom": "New laptop cannot obtain an IP address",
        "topology_note": "DHCP server on Router1, Laptop connected via Switch",
        "concept_tag": "DHCP",
        "severity": "High",
        "show_outputs": "Router1#show ip dhcp pool\n\nPool LOCAL_LAN :\n Utilization mark (high/low)    : 100 / 0\n Subnet size (first/next)       : 0 / 0 \n Total addresses                : 254\n Leased addresses               : 254\n Excluded addresses             : 0\n Pending event                  : none\n",
        "expected_fault": "DHCP pool is exhausted (254 leased out of 254)",
        "osi_layer": "Layer 7"
    },
    {
        "case_id": "CASE-006",
        "symptom": "Clients on VLAN 20 are getting APIPA addresses (169.254.x.x)",
        "topology_note": "Router provides inter-VLAN routing and DHCP. VLAN 20 is on Gi0/0.20",
        "concept_tag": "DHCP",
        "severity": "High",
        "show_outputs": "Router#show run interface GigabitEthernet0/0.20\nBuilding configuration...\n\nCurrent configuration : 112 bytes\n!\ninterface GigabitEthernet0/0.20\n encapsulation dot1Q 20\n ip address 192.168.20.1 255.255.255.0\nend\n",
        "expected_fault": "Missing ip helper-address if DHCP is external, or DHCP pool for VLAN 20 is missing (implied by no response and APIPA)",
        "osi_layer": "Layer 7"
    },
    # 4. DNS failure
    {
        "case_id": "CASE-007",
        "symptom": "Users can ping 8.8.8.8 but cannot browse www.google.com",
        "topology_note": "Host configured via static IP",
        "concept_tag": "DNS",
        "severity": "Medium",
        "show_outputs": "Host>ipconfig /all\n\nIPv4 Address. . . . . . . . . . . : 10.1.1.50\nSubnet Mask . . . . . . . . . . . : 255.255.255.0\nDefault Gateway . . . . . . . . . : 10.1.1.1\nDNS Servers . . . . . . . . . . . : \n",
        "expected_fault": "No DNS server configured on the host",
        "osi_layer": "Layer 7"
    },
    {
        "case_id": "CASE-008",
        "symptom": "Router cannot resolve hostnames for pings",
        "topology_note": "Router needs to reach update server by name",
        "concept_tag": "DNS",
        "severity": "Low",
        "show_outputs": "Router#show run | inc ip domain\nno ip domain-lookup\n",
        "expected_fault": "ip domain-lookup is disabled",
        "osi_layer": "Layer 7"
    },
    # 5. Static/dynamic routing issues
    {
        "case_id": "CASE-009",
        "symptom": "Branch office cannot reach HQ subnets",
        "topology_note": "Branch Router connected to ISP, HQ subnet is 10.0.0.0/8",
        "concept_tag": "Routing",
        "severity": "Critical",
        "show_outputs": "BranchRouter#show ip route\nGateway of last resort is not set\n\n      192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks\nC        192.168.1.0/24 is directly connected, GigabitEthernet0/0\nL        192.168.1.1/32 is directly connected, GigabitEthernet0/0\n",
        "expected_fault": "Missing default route or static route to HQ subnet",
        "osi_layer": "Layer 3"
    },
    {
        "case_id": "CASE-010",
        "symptom": "OSPF neighbor relationship not forming between R1 and R2",
        "topology_note": "R1 and R2 connected on 10.1.1.0/30",
        "concept_tag": "Routing",
        "severity": "High",
        "show_outputs": "R1#show ip ospf interface brief\nInterface    PID   Area            IP Address/Mask    Cost  State Nbrs F/C\nGi0/0        1     0               10.1.1.1/30        1     DR    0/0\n\nR1#show run | section router ospf\nrouter ospf 1\n network 10.1.1.0 0.0.0.255 area 0\n",
        "expected_fault": "OSPF neighbor state stuck, potentially mismatched timers or MTU, but here just no neighbors. Let's make it an area mismatch.\nR2#show run | section router ospf\nrouter ospf 1\n network 10.1.1.0 0.0.0.3 area 1",
        "osi_layer": "Layer 3"
    },
    # 6. ACL blocking
    {
        "case_id": "CASE-011",
        "symptom": "Web server in DMZ cannot be reached from outside on port 80",
        "topology_note": "Edge router has inbound ACL applied on WAN interface",
        "concept_tag": "ACL",
        "severity": "High",
        "show_outputs": "EdgeRouter#show access-lists\nExtended IP access list 100\n    10 permit tcp any host 10.1.1.5 eq 443\n    20 deny ip any any (150 matches)\nEdgeRouter#show ip int Gi0/0 | inc access list\n  Inbound  access list is 100\n  Outbound access list is not set\n",
        "expected_fault": "ACL 100 permits HTTPS (443) but implicitly denies HTTP (80)",
        "osi_layer": "Layer 3"
    },
    {
        "case_id": "CASE-012",
        "symptom": "Cannot SSH to Router from admin subnet",
        "topology_note": "Admin subnet is 192.168.100.0/24",
        "concept_tag": "ACL",
        "severity": "Medium",
        "show_outputs": "Router#show run | section line vty\nline vty 0 4\n access-class 10 in\n login local\n transport input ssh\nRouter#show access-lists 10\nStandard IP access list 10\n    10 permit 192.168.200.0, wildcard bits 0.0.0.255\n",
        "expected_fault": "VTY lines restricted to 192.168.200.0/24, admin subnet is blocked",
        "osi_layer": "Layer 3"
    },
    # 7. NAT/PAT misconfig
    {
        "case_id": "CASE-013",
        "symptom": "Internal users cannot access the internet, but router can ping 8.8.8.8",
        "topology_note": "NAT Overload configured on Edge Router",
        "concept_tag": "NAT",
        "severity": "High",
        "show_outputs": "EdgeRouter#show ip nat statistics\nTotal active translations: 0 (0 static, 0 dynamic; 0 extended)\nEdgeRouter#show run interface Gi0/1\ninterface GigabitEthernet0/1\n description WAN\n ip address 203.0.113.2 255.255.255.252\n ip nat outside\nEdgeRouter#show run interface Gi0/0\ninterface GigabitEthernet0/0\n description LAN\n ip address 192.168.1.1 255.255.255.0\n",
        "expected_fault": "Missing 'ip nat inside' on the LAN interface Gi0/0",
        "osi_layer": "Layer 4"
    },
    {
        "case_id": "CASE-014",
        "symptom": "NAT translations are not occurring for Guest VLAN",
        "topology_note": "Guest VLAN is 192.168.5.0/24",
        "concept_tag": "NAT",
        "severity": "Medium",
        "show_outputs": "Router#show access-lists 1\nStandard IP access list 1\n    10 permit 192.168.1.0, wildcard bits 0.0.0.255\nRouter#show run | inc ip nat inside source\nip nat inside source list 1 interface GigabitEthernet0/1 overload\n",
        "expected_fault": "NAT ACL 1 does not include the Guest VLAN subnet (192.168.5.0/24)",
        "osi_layer": "Layer 4"
    },
    # 8. Trunk/native VLAN mismatch
    {
        "case_id": "CASE-015",
        "symptom": "CDP logs show native VLAN mismatch",
        "topology_note": "Switch1 Gi0/1 connected to Switch2 Gi0/1",
        "concept_tag": "Trunking",
        "severity": "Medium",
        "show_outputs": "Switch1#show interfaces trunk\n\nPort        Mode         Encapsulation  Status        Native vlan\nGi0/1       on           802.1q         trunking      99\n\nSwitch2#show interfaces trunk\n\nPort        Mode         Encapsulation  Status        Native vlan\nGi0/1       on           802.1q         trunking      1\n",
        "expected_fault": "Native VLAN mismatch (Switch1 uses 99, Switch2 uses 1)",
        "osi_layer": "Layer 2"
    },
    {
        "case_id": "CASE-016",
        "symptom": "VLAN 20 traffic not crossing inter-switch link",
        "topology_note": "Link between switches should carry all VLANs",
        "concept_tag": "Trunking",
        "severity": "High",
        "show_outputs": "Switch1#show interfaces trunk\n\nPort        Mode         Encapsulation  Status        Native vlan\nGi0/1       on           802.1q         trunking      1\n\nPort        Vlans allowed on trunk\nGi0/1       1-10,30-4094\n",
        "expected_fault": "VLAN 20 is missing from the allowed VLANs list on the trunk",
        "osi_layer": "Layer 2"
    },
    # 9. Sub-interface administratively down
    {
        "case_id": "CASE-017",
        "symptom": "Router-on-a-stick not routing for VLAN 10",
        "topology_note": "VLAN 10 sub-interface is Gi0/0.10",
        "concept_tag": "Interface",
        "severity": "High",
        "show_outputs": "Router#show ip interface brief\nInterface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0     unassigned      YES unset  up                    up      \nGigabitEthernet0/0.10  192.168.10.1    YES manual administratively down down    \n",
        "expected_fault": "Sub-interface Gi0/0.10 is administratively down (needs 'no shutdown')",
        "osi_layer": "Layer 1"
    },
    {
        "case_id": "CASE-018",
        "symptom": "WAN link is down after recent maintenance",
        "topology_note": "Serial interface to ISP",
        "concept_tag": "Interface",
        "severity": "Critical",
        "show_outputs": "Router#show ip interface brief\nInterface              IP-Address      OK? Method Status                Protocol\nSerial0/0/0            203.0.113.1     YES manual administratively down down    \n",
        "expected_fault": "Serial0/0/0 interface is administratively down",
        "osi_layer": "Layer 1"
    },
    # 10. Wireless/guest network isolation issues
    {
        "case_id": "CASE-019",
        "symptom": "Guests can access internal company servers",
        "topology_note": "Guest subnet is 172.16.0.0/24, Internal is 10.0.0.0/8",
        "concept_tag": "Security",
        "severity": "High",
        "show_outputs": "Router#show access-lists GUEST_ACL\nExtended IP access list GUEST_ACL\n    10 permit ip 172.16.0.0 0.0.0.255 any\nRouter#show ip int Gi0/1.50 | inc access list\n  Inbound  access list is GUEST_ACL\n  Outbound access list is not set\n",
        "expected_fault": "Guest ACL permits all traffic to 'any', allowing access to internal networks instead of denying it",
        "osi_layer": "Layer 3"
    },
    {
        "case_id": "CASE-020",
        "symptom": "Wireless clients cannot get IP addresses",
        "topology_note": "WLC connected to switch port Gi1/0/1",
        "concept_tag": "Wireless",
        "severity": "High",
        "show_outputs": "Switch#show run interface GigabitEthernet1/0/1\ninterface GigabitEthernet1/0/1\n switchport mode access\n switchport access vlan 10\n",
        "expected_fault": "WLC port is configured as access mode instead of trunk, blocking multiple wireless VLANs",
        "osi_layer": "Layer 2"
    },
    # 11. Duplicate IP address
    {
        "case_id": "CASE-021",
        "symptom": "Intermittent connectivity drops for Server A",
        "topology_note": "Server A has static IP 192.168.1.100",
        "concept_tag": "IP Addressing",
        "severity": "Critical",
        "show_outputs": "Router#show ip arp | inc 192.168.1.100\nInternet  192.168.1.100           0   0000.aaaa.bbbb  ARPA   GigabitEthernet0/0\nInternet  192.168.1.100           0   0000.cccc.dddd  ARPA   GigabitEthernet0/0\n*Mar  1 00:15:22.333: %IP-4-DUPADDR: Duplicate address 192.168.1.100 on GigabitEthernet0/0\n",
        "expected_fault": "Duplicate IP address 192.168.1.100 detected in ARP cache and logs",
        "osi_layer": "Layer 3"
    },
    {
        "case_id": "CASE-022",
        "symptom": "Cannot assign IP to new router interface",
        "topology_note": "Configuring Gi0/1 with 10.1.1.1/24",
        "concept_tag": "IP Addressing",
        "severity": "Medium",
        "show_outputs": "Router#show ip interface brief\nInterface              IP-Address      OK? Method Status                Protocol\nGigabitEthernet0/0     10.1.1.254      YES manual up                    up      \nGigabitEthernet0/1     unassigned      YES unset  up                    up      \nRouter(config-if)#ip address 10.1.1.1 255.255.255.0\n% 10.1.1.0 overlaps with GigabitEthernet0/0\n",
        "expected_fault": "Overlapping subnet (duplicate IP space) on Gi0/0 and Gi0/1",
        "osi_layer": "Layer 3"
    },
    # 12. Wrong subnet mask
    {
        "case_id": "CASE-023",
        "symptom": "Host .250 cannot ping host .10 in the same intended /24 subnet",
        "topology_note": "Host A 192.168.1.250, Host B 192.168.1.10",
        "concept_tag": "IP Addressing",
        "severity": "Medium",
        "show_outputs": "HostA>ipconfig\n\nIPv4 Address. . . . . . . . . . . : 192.168.1.250\nSubnet Mask . . . . . . . . . . . : 255.255.255.128\nDefault Gateway . . . . . . . . . : 192.168.1.1\n",
        "expected_fault": "Wrong subnet mask (255.255.255.128) places Host A in a different subnet than Host B",
        "osi_layer": "Layer 3"
    },
    {
        "case_id": "CASE-024",
        "symptom": "Point-to-point link wasting addresses",
        "topology_note": "WAN link between R1 and R2",
        "concept_tag": "IP Addressing",
        "severity": "Low",
        "show_outputs": "R1#show run interface Serial0/0/0\ninterface Serial0/0/0\n ip address 10.0.0.1 255.255.255.0\n",
        "expected_fault": "Using /24 (255.255.255.0) instead of /30 (255.255.255.252) for a point-to-point link",
        "osi_layer": "Layer 3"
    },
    # Mixed/Additional cases to reach 30
    {
        "case_id": "CASE-025",
        "symptom": "No connectivity across switch link",
        "topology_note": "Switch port connecting to another switch",
        "concept_tag": "Trunking",
        "severity": "High",
        "show_outputs": "Switch1#show interfaces Fa0/24 switchport\nName: Fa0/24\nSwitchport: Enabled\nAdministrative Mode: static access\nOperational Mode: static access\n",
        "expected_fault": "Port Fa0/24 is configured as static access instead of trunk",
        "osi_layer": "Layer 2"
    },
    {
        "case_id": "CASE-026",
        "symptom": "OSPF routes not appearing in routing table",
        "topology_note": "R1 OSPF configuration",
        "concept_tag": "Routing",
        "severity": "Medium",
        "show_outputs": "R1#show ip protocols\nRouting Protocol is \"ospf 1\"\n  Outgoing update filter list for all interfaces is not set\n  Incoming update filter list for all interfaces is not set\n  Router ID 10.0.0.1\n  Number of areas in this router is 1. 1 normal 0 stub 0 nssa\n  Routing for Networks:\n    10.0.0.0 0.255.255.255 area 0\n",
        "expected_fault": "Wildcard mask is extremely broad (0.255.255.255) instead of specific (e.g., 0.0.0.255), possibly encompassing wrong interfaces",
        "osi_layer": "Layer 3"
    },
    {
        "case_id": "CASE-027",
        "symptom": "Cannot telnet to switch for management",
        "topology_note": "Switch management IP 10.1.1.10",
        "concept_tag": "Security",
        "severity": "Medium",
        "show_outputs": "Switch#show run | section line vty\nline vty 0 4\n login\n transport input ssh\n",
        "expected_fault": "Telnet is implicitly disabled because transport input is restricted to ssh only",
        "osi_layer": "Layer 7"
    },
    {
        "case_id": "CASE-028",
        "symptom": "DHCP clients receive wrong gateway",
        "topology_note": "Router1 acts as DHCP server, Router1 LAN IP is 192.168.10.1",
        "concept_tag": "DHCP",
        "severity": "High",
        "show_outputs": "Router1#show run | section ip dhcp pool\nip dhcp pool LAN\n network 192.168.10.0 255.255.255.0\n default-router 192.168.10.254\n dns-server 8.8.8.8\n",
        "expected_fault": "Default router in DHCP pool is configured as .254 instead of .1",
        "osi_layer": "Layer 7"
    },
    {
        "case_id": "CASE-029",
        "symptom": "Port security triggered, port err-disabled",
        "topology_note": "User plugged in a mini-switch to their wall jack",
        "concept_tag": "Security",
        "severity": "High",
        "show_outputs": "Switch#show interfaces Fa0/5 status\n\nPort      Name               Status       Vlan       Duplex  Speed Type\nFa0/5                        err-disabled 10         auto    auto  10/100BaseTX\nSwitch#show port-security interface Fa0/5\nPort Security              : Enabled\nPort Status                : Secure-down\nViolation Mode             : Shutdown\nMaximum MAC Addresses      : 1\nTotal MAC Addresses        : 2\n",
        "expected_fault": "Port security violation: more than 1 MAC address learned (Total MAC: 2 > Max: 1), causing err-disable",
        "osi_layer": "Layer 2"
    },
    {
        "case_id": "CASE-030",
        "symptom": "Inter-VLAN routing failing for VLAN 30",
        "topology_note": "Router with multiple sub-interfaces",
        "concept_tag": "VLAN",
        "severity": "High",
        "show_outputs": "Router#show run interface Gi0/0.30\ninterface GigabitEthernet0/0.30\n encapsulation dot1Q 40\n ip address 192.168.30.1 255.255.255.0\n",
        "expected_fault": "Sub-interface dot1Q encapsulation is mismatched (VLAN 40 tag instead of VLAN 30 tag)",
        "osi_layer": "Layer 2"
    }
]

with open(r"d:\CISCO\netsage-ai\data\cases.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["case_id", "symptom", "topology_note", "concept_tag", "severity", "show_outputs", "expected_fault", "osi_layer"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cases)

print("Created cases.csv")
