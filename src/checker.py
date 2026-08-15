import re

def run_checker(show_outputs: str) -> dict:
    """
    Deterministic rule-based checker for common Cisco networking faults.
    Returns a dict with status, flags, and details.
    """
    flags = []
    details = []

    # Check 1: Administratively down interfaces
    admin_down_matches = re.findall(r'(\S+)\s+(?:[\d\.]+|unassigned)\s+YES\s+(?:manual|unset)\s+administratively down', show_outputs)
    if admin_down_matches:
        flags.append("ADMIN_DOWN")
        details.append(f"Interfaces administratively down: {', '.join(admin_down_matches)}")

    # Check 2: Duplicate IP Addresses (from ARP or logs)
    dup_ip_matches = re.findall(r'Duplicate address ([\d\.]+)', show_outputs)
    if dup_ip_matches:
        flags.append("DUPLICATE_IP")
        details.append(f"Duplicate IP addresses detected: {', '.join(set(dup_ip_matches))}")

    # Check 3: Overlapping subnets error
    overlap_matches = re.findall(r'([\d\.]+)\s+overlaps with\s+(\S+)', show_outputs)
    if overlap_matches:
        flags.append("OVERLAPPING_SUBNETS")
        details.append(f"Overlapping subnets detected: {', '.join([f'{ip} on {intf}' for ip, intf in overlap_matches])}")

    # Check 4: Missing NAT commands
    if "ip nat outside" in show_outputs and "ip nat inside" not in show_outputs:
        if "interface" in show_outputs: # Make sure we are looking at interface configs
            flags.append("MISSING_NAT_INSIDE")
            details.append("Detected 'ip nat outside' but no 'ip nat inside' configured.")

    if "ip nat inside" in show_outputs and "ip nat outside" not in show_outputs and not show_outputs.count("ip nat outside"):
         if "interface" in show_outputs:
             flags.append("MISSING_NAT_OUTSIDE")
             details.append("Detected 'ip nat inside' but no 'ip nat outside' configured.")

    # Check 5: Port Security Violation
    if "err-disabled" in show_outputs and "Port Security" in show_outputs and "Secure-down" in show_outputs:
        flags.append("PORT_SECURITY_VIOLATION")
        details.append("Port security violation detected causing err-disable state.")

    status = "ERRORS_DETECTED" if flags else "NO_ERRORS_DETECTED"

    return {
        "status": status,
        "flags": flags,
        "details": details
    }

if __name__ == "__main__":
    sample_output = """
    Router#show ip interface brief
    Interface              IP-Address      OK? Method Status                Protocol
    GigabitEthernet0/0     192.168.1.1     YES manual administratively down down
    GigabitEthernet0/1     10.0.0.1        YES manual up                    up
    """
    result = run_checker(sample_output)
    print("Checker Result:")
    print(result)
