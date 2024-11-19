# **TorBox - Tor Control Go Implementation**

--- 
#### Note: This project has been written for the [TorBox](https://torbox.ch) project. It is a part of the TorBox project and is used to control the Tor instance running on the TorBox.


---

### **Overview**

The `TorControl` Go implementation provides a library to interact with the Tor control port, enabling control and monitoring of circuits, streams, nodes, and configurations. It is designed for developers building custom applications with Tor integration.

This library supports:
- Circuit management
- Node information retrieval
- Configuration updates
- Event monitoring

---

### **Features**

- **Circuit Management**: Retrieve, extend, and close Tor circuits.
- **Node Information**: Fetch detailed information about specific Tor nodes.
- **Configuration Updates**: Modify and reload Tor configurations programmatically.
- **Event Monitoring**: Real-time monitoring of bandwidth, streams, and circuit events.
- **Authentication**: Securely connect to the Tor control port using a password.

---

### **Requirements**

1. **Tor**:
    - Installed and running locally or on a remote server.
    - Control port enabled in `torrc`:
      ```bash
      ControlPort 9051
      HashedControlPassword <your_password_hash>
      ```

2. **Go**:
    - Version 1.18 or later.

3. **Dependencies**:
    - None (uses the Go standard library).

---

### **Installation**

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd tor-control
   ```

2. Build the project:
   ```bash
   go build .
   ```

3. Import the library in your project:
   ```go
   import "path/to/torcontrol"
   ```

---

### **Usage**

#### **Initialization**

```go
client, err := torcontrol.NewClient("127.0.0.1", 9051, "your_password")
if err != nil {
	log.Fatalf("Failed to connect to Tor: %v", err)
}
defer client.Close()
```

---

### **Examples**

#### **1. Retrieve Active Circuits**
```go
circuits, err := client.GetCircuits()
if err != nil {
	log.Fatalf("Failed to get circuits: %v", err)
}

fmt.Println("Active Circuits:")
for _, circuit := range circuits {
	fmt.Printf("ID: %s, Status: %s, Path: %s\n", circuit.ID, circuit.Status, circuit.Path)
}
```

---

#### **2. Monitor Bandwidth Events**
```go
err = client.SetEvents([]string{"BW"})
if err != nil {
	log.Fatalf("Failed to enable bandwidth events: %v", err)
}

fmt.Println("Monitoring bandwidth events...")
for event := range client.WatchBandwidth() {
	fmt.Printf("Time: %s, Read: %s bytes, Written: %s bytes\n", event.Time, event.Read, event.Written)
}
```

---

#### **3. Retrieve Node Information**
```go
fingerprint := "89EEAFA5830FA551516091524654BDE14792A812"
nodeInfo, err := client.GetNodeInfo(fingerprint)
if err != nil {
	log.Fatalf("Failed to get node info: %v", err)
}

fmt.Printf("Node Info:\nFingerprint: %s\nIP: %s\nPort: %d\nFlags: %v\n",
	nodeInfo.Fingerprint, nodeInfo.IP, nodeInfo.Port, nodeInfo.Flags)
```

---

#### **4. Update Configuration**
```go
err = client.SetConf(map[string]string{
	"DisableNetwork": "1",
})
if err != nil {
	log.Fatalf("Failed to set configuration: %v", err)
}

fmt.Println("Network disabled.")
```

---

### **Testing**

1. Run the provided test cases in `main.go`:
   ```bash
   go run main.go
   ```

2. Verify Tor control responses using Telnet:
   ```bash
   telnet 127.0.0.1 9051
   AUTHENTICATE "your_password"
   GETINFO circuit-status
   ```

---

### **Security Considerations**

1. **Control Port Access**:
    - Ensure the control port (`9051`) is accessible only locally or from trusted machines.
    - Use a strong password or cookie for authentication.

2. **Exit Node Risks**:
    - Tor exit nodes can observe unencrypted traffic. Use end-to-end encryption (e.g., HTTPS) to mitigate risks.


