import pytest

from tor_control import TORBOX_IP_MINI, TorControl, TOR_CONTROL_PASSWORD


# Test the TorControl class
def test_tor_control():
    tor_control = TorControl(torbox_ip=TORBOX_IP_MINI)
    tor_control.authenticate(TOR_CONTROL_PASSWORD)
    tor_version = tor_control.send_command("GETINFO version")
    assert tor_version.startswith("250")
    assert tor_version.endswith("250 OK\r\n")
    print("Tor version: ", tor_version)
    tor_control.socket.close()
    assert tor_control.socket._closed

# Test the circuit list
def test_get_circuits():
    tor_control = TorControl(torbox_ip=TORBOX_IP_MINI)
    tor_control.authenticate(TOR_CONTROL_PASSWORD)
    circuits = tor_control.get_circuits()
    assert isinstance(circuits, list)
    assert len(circuits) > 0
    for circuit in circuits:
        assert isinstance(circuit, dict)
        assert "id" in circuit
        assert "status" in circuit
        assert "path" in circuit
    tor_control.socket.close()
    assert tor_control.socket._closed