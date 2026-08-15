# NetSage AI - Model Audit Log

This log tracks the decisions made by human reviewers on the AI-generated diagnoses. This ensures a human-in-the-loop process where AI acts only as a decision-support system.

| Timestamp | Case ID | AI Root Cause | AI Confidence | Human Decision | Human Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 2024-05-10 10:15:22 | CASE-001 | Ports are in different VLANs (Fa0/1 in VLAN 1, Fa0/2 in VLAN 20). | 0.95 | Edited | Corrected the VLAN number. The output shows Fa0/2 is in VLAN 10, not 20. |
| 2024-05-10 11:30:45 | CASE-015 | Native VLAN mismatch (Switch1 uses 99, Switch2 uses 1). | 0.88 | Approved | Good catch by the AI. Approved without changes. |
| 2024-05-11 09:05:12 | CASE-005 | DHCP pool is exhausted (254 leased out of 254). | 0.92 | Approved | Spot on. Will increase the pool size manually. |
| 2024-05-12 14:22:10 | CASE-017 | Sub-interface Gi0/0.10 is administratively down. | 1.00 | Rejected | AI flagged this, but this interface was intentionally shut down for maintenance. No fix needed yet. |
| 2024-05-13 16:40:05 | CASE-011 | ACL 100 permits HTTPS (443) but implicitly denies HTTP (80). | 0.85 | Edited | AI suggested removing the ACL. Instead, I edited the commands to add a permit statement for port 80. |

| 2026-08-15 22:22:04 | CASE-001 | PC1 and PC2 are in different VLANs on the same switch, preventing Layer 2 communication. PC1 is in VLAN 1 (default), while PC2 is in VLAN 10 (Sales). | 1.00 | Approved | Approved as suggested. |
| 2026-08-15 22:26:42 | TEST-ID | Test Cause | 1.00 | Approved | Test Notes |
| 2026-08-15 22:31:42 | CASE-030 | The sub-interface GigabitEthernet0/0.30 is configured with VLAN 40 encapsulation (dot1Q 40) but is assigned an IP address for VLAN 30 (192.168.30.1/24). This mismatch prevents inter-VLAN routing for VLAN 30. | 1.00 | Approved | Approved as suggested. |