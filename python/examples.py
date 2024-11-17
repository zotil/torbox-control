#------------------------
# EXAMPLES FROM README
#------------------------
# circuits = tor_control.get_circuits()
# for circuit in circuits:
#     print(f"Circuit ID: {circuit['id']} Purpose: {circuit['purpose']} Status: {circuit['status']}")

# node_info = tor_control.get_node_info("89EEAFA5830FA551516091524654BDE14792A812")  # fake fingerprint -> error
# print(node_info)

# print(tor_control.get_conf("SocksPort"))
# tor_control.set_conf(DisableNetwork="1")
# tor_control.reload_config()

#-----------------
# tor_version = tor_control.send_command("GETINFO version")
# print("Tor version: ", tor_version)

# Read bandwidth
# tor_control.set_bandwidth(status=True)
# for data in tor_control.bandwidth_events():
#     print("BW ", data)

# Get circuits list
# circuits = tor_control.get_circuits()
# from pprint import pprint
# print(circuits)

# Get outbound connections
# connections = tor_control.get_outbound_connections()
# for conn in connections:
#     print(f"Connection to {conn['node']['router']['ip']} ({conn['fingerprint']}) is {conn['status']}")

# print(tor_control.get_log())
# for c in tor_control.watch_circuits():
#     print(c)