## TorBox - Tor Control
#### Note: This project has been written for the [TorBox](https://torbox.ch) project. It is a part of the TorBox project and is used to control the Tor instance running on the TorBox.
### **TorControl Class**

---

### **Overview**

The `TorControl` class is a Python implementation for interacting with the Tor control port. It provides functionality to manage Tor circuits, nodes, configurations, and events, allowing for complete control and monitoring of a Tor instance.

---

### **Features**

- **Authentication:** Authenticate with the Tor control port using a password.
- **Circuits Management:**
    - Retrieve and format active circuits.
    - Extend or close circuits.
- **Node Information:**
    - Fetch detailed information about Tor nodes using their fingerprints.
- **Configuration Management:**
    - Modify, reset, and reload Tor configurations.
    - Save and load configurations from files.
- **Event Monitoring:**
    - Monitor bandwidth, circuit, and events in real-time.
- **Outbound Connections:**
    - Fetch active outbound connections using `GETINFO orconn-status`.
- **Bandwidth Management:**
    - Enable or disable bandwidth event reporting.
    - Retrieve bandwidth usage in real-time.

---

### **Requirements**

- Tor must be installed and running with the `ControlPort` enabled.
- A configured password or cookie for control port authentication.
- Python 3.6 or later.

---

### **Installation**

1. Install Tor:
   ```bash
   sudo apt install tor
   ```
2. Enable the control port in `torrc`:
   ```bash
   ControlPort 9051
   HashedControlPassword <your_password_hash>
   ```
3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

---

### **Initialization**

To initialize the `TorControl` class:

```python
from tor_control import TORBOX_IP_WIFI, TorControl

tor_control = TorControl(timeout=5, torbox_ip=TORBOX_IP_WIFI)
tor_control.authenticate("password")
```

---

### **Methods**

#### **1. Authentication**
- **`authenticate()`**
    - Authenticates with the Tor control port using the configured password.

#### **2. Circuits**
- **`get_circuits()`**
    - Retrieves a list of active circuits and their details.
- **`extend_circuit(circuit_id, *nodes)`**
    - Extends a circuit with additional nodes.
- **`close_circuit(circuit_id)`**
    - Closes a specified circuit.

#### **5. Nodes**
- **`get_node_info(fingerprint)`**
    - Retrieves detailed information about a node using its fingerprint.

#### **6. Configuration**
- **`set_conf(**kwargs)`**
    - Sets configuration parameters.
- **`reset_conf(*keys)`**
    - Resets configuration parameters to defaults.
- **`reload_config()`**
    - Reloads the Tor configuration file.

#### **7. Events**
- **`set_bandwidth(status: bool)`**
    - Enables or disables bandwidth event reporting.
- **`bandwidth_events()`**
    - Monitors bandwidth events in real-time.
- **`get_outbound_connections()`**
    - Retrieves active outbound connections.

---

### **Examples**

#### **1. Retrieve Active Circuits**
```python
circuits = tor_control.get_circuits()
for circuit in circuits:
    print(f"Circuit ID: {circuit['id']}, Status: {circuit['status']}")
```

#### **2. Monitor Bandwidth Events**
```python
tor_control.set_bandwidth(True)
try:
    for event in tor_control.bandwidth_events():
        print(event)
except KeyboardInterrupt:
    print("Stopped monitoring bandwidth events.")
```

#### **3. Get Node Information**
```python
node_info = tor_control.get_node_info("89EEAFA5830FA551516091524654BDE14792A812")
print(node_info)
```

#### **4. Manage Configuration**
```python
tor_control.set_conf(DisableNetwork="1")
tor_control.reload_config()
```

---

### **Error Handling**

- The `TorControl` class raises exceptions for failed commands or authentication issues.
- Examples:
    - `Authentication failed: 515 Authentication required`
    - `Failed to set bandwidth event status: 552 Command not recognized`

