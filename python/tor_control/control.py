import socket as _socket
import logging
from functools import wraps
from tor_control import TORBOX_IP_WIFI, TOR_CONTROL_PORT, TOR_CONTROL_PASSWORD

logger = logging.getLogger("tor_control")
logging.basicConfig(level=logging.DEBUG)


class TorControl:
    """
    Tor control class to interact with the Tor control port.
    """

    event_bandwidth = False

    def __init__(self, timeout=5, torbox_ip=TORBOX_IP_WIFI):
        self.socket = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
        self.socket .settimeout(timeout)  # Set the configurable timeout
        self.socket .connect((torbox_ip, TOR_CONTROL_PORT))

    # authenticate socket
    def authenticate(self, password):
        """
        Authenticate with the Tor control port using the configured password.

        Raises:
            Exception: If the authentication fails.

        Returns:
            None
        """
        # Authenticate with the control port
        self.socket.send("AUTHENTICATE \"{}\"\r\n".format(password).encode())
        response = self.socket.recv(1024).decode()

        if not response.startswith("250 OK"):
            raise Exception("Authentication failed: {}".format(response.strip()))

        return True

    # Send command to tor control
    def send_command(self, command) -> str:
        """
        Send a command to the Tor control socket and return the response.

        Args:
            command (str): The command to send to the Tor control socket.

        Returns:
            str: The response from the Tor control socket.
        """
        # Send the specified command
        self.socket.sendall(f"{command}\r\n".encode())

        # Collect and return the response
        response = ""
        while True:
            try:
                data = self.socket.recv(1024).decode()
                response += data
                # Check if the response has reached the end
                if "\r\n250 " in response or response.endswith("250 OK\r\n"):
                    break
            # Except timeout socket
            except TimeoutError:
                raise Exception("Timeout waiting for response from Tor control socket")

        return response

    # Get formatted circuits
    def get_circuits(self):
        """
        Retrieve the list of circuits from the Tor control socket.

        Returns:
            list: A list of circuits with their details.
        """
        response = self.send_command("GETINFO circuit-status")

        # Initialize a list to store the circuit information
        circuits = []

        # Process each line of the response
        for line in response.splitlines():
            if line.startswith("250+circuit-status="):
                # Skip the header line
                continue
            elif line.startswith("250 OK"):
                # Stop processing at the end of the response
                break
            elif line.strip() and line.strip() != ".":
                # Add non-empty, non-terminal lines to the circuit list
                circuits.append(line.strip())

        # Format circuits
        circuits_list = []
        if len(circuits) <2:
            return []

        for circuit in circuits:
            c = {}
            parts = circuit.split(" ")
            c['id'] = parts[0].replace("250-circuit-status=", "")
            c['status'] = parts[1]
            c['path'] = parts[2]
            c['nodes'] = []
            for idx, node in enumerate(c['path'].split(",")):
                fingerprint, name = node.split("~")
                fingerprint = fingerprint.replace("$", "")
                node_info = self.get_node_info(fingerprint)
                # Check if this node is the guard, exit or middle
                if idx == 0:
                    name = "Guard"
                elif idx == len(c['path'].split(",")) - 1:
                    name = "Exit"
                    if idx == 1:
                        name = "Extending"
                    elif idx == 2:
                        name = "Exit"
                else:
                    name = "Middle"

                c['nodes'].append({
                    "name": name,
                    "fingerprint": fingerprint,
                    "ip": node_info['router']['ip'],
                    "ip_port": node_info['router']['ip_port']
                })

            c['build_flags'] = parts[3].replace("BUILD_FLAGS=", "")
            c['purpose'] = parts[4].replace("PURPOSE=", "")
            c['time_created'] = parts[5].replace("TIME_CREATED=", "")
            circuits_list.append(c)

        return circuits_list

    # Get node info
    def get_node_info(self, fingerprint):
        """
        Retrieve information about a Tor node using its fingerprint.

        :param fingerprint: The fingerprint of the Tor node.
        :return: A dictionary containing information about the Tor node.

        Example response:
        {
            'router': {
                'nickname': '$NICKNAME',
                'fingerprint': '$FINGERPRINT',
                'pub_key': '$PUBKEY',
                'exp_date': '$EXPIRATION',
                'ip': '$IP',
                'ip_port': '$PORT'
            },
            'status': {
                'status': '$STATUS',
                'flags': ['$FLAG1', '$FLAG2', ...]
            },
            'bandwidth': {
                'bandwidth': '$BANDWIDTH'
            }
        }
        """
        response = self.send_command(f"GETINFO ns/id/{fingerprint}")
        node_info = {}
        router = None
        status = None
        bandwidth = None

        for line in response.splitlines():
            # r: Información sobre el router (nodo) en la red Tor.
            # s: Estado del nodo (por ejemplo, si es un nodo de salida, guardia, etc.).
            # w: Información sobre el ancho de banda del nodo.
            if line.startswith("250+"):
                # Skip the header line
                continue
            elif line.startswith("250 OK"):
                # Stop processing at the end of the response
                break
            elif line.strip() and line.strip() != ".":
                parts = line.split(" ")

                if parts[0] == "r":
                    # r: Information about the router (node) in the Tor network.
                    # Example: r $NICKNAME $IP $ORPORT $SOCKSPORT $DIRPORT
                    router = {
                        'nickname': parts[1],
                        'fingerprint': parts[2],
                        'pub_key': parts[3],
                        'exp_date': "{} {}".format(parts[4], parts[5]),
                        'ip': parts[6],
                        'ip_port': parts[7]
                    }

                if parts[0] == "s":
                    # s: Node status (e.g., if it is an exit node, guard, etc.).
                    # Example: s $STATUS $FLAGS
                    status = {
                        'status': parts[1],
                        'flags': parts[2:]
                    }

                if parts[0] == "w":
                    # w: Information about the node's bandwidth.
                    # Example: w Bandwidth=$BANDWIDTH
                    bandwidth = {
                        'bandwidth': parts[1].split("=")[1]
                    }

                if parts[0] == "a":
                    # a: Information about the node's IP address.
                    # Example: a [$IPv6]:$PORT
                    ip = parts[1].rsplit(":", 1)
                    router['ipv6'] = ip[0]
                    router['ip_port'] = ip[1]


        node_info = {
            'router': router,
            'status': status,
            'bandwidth': bandwidth
        }

        return node_info

    def set_bandwidth(self, status: bool):
        """
        Set the bandwidth event status on the Tor control socket.
        """

        # Send command
        if status:
            self.socket.sendall("SETEVENTS BW\r\n".encode())
        else:
            self.socket.sendall("SETEVENTS -BW\r\n".encode())

        response = self.socket.recv(1024).decode()
        if not response.startswith("250 OK"):
            raise Exception("Failed to set bandwidth event status: {}".format(response.strip()))

        self.event_bandwidth = status

    def bandwidth_events(self):
        # Stay listening for events
        while True:
            response = self.socket.recv(1024).decode().strip()
            if response.startswith("650 BW"):
                # Remove "650 BW" and split the event data
                yield response[7:].split(" ")

    def get_outbound_connections(self):
        """
        Fetches the current outbound connections using GETINFO orconn-status.

        Args:
            socket (socket): Authenticated socket connection.

        Returns:
            list: A list of active outbound connections with their statuses.
        """
        response = self.send_command("GETINFO orconn-status")
        connections = []
        for line in response.splitlines():
            if line.startswith("250+") or line.startswith("250 OK") or line.strip() == ".":
                continue
            # Example line: $FINGERPRINT CONNECTED "192.0.2.1:9001"
            parts = line.split(" ", 2)
            fingerprint, nickname = parts[0].replace("$", "").split("~")
            status = parts[1]
            connection = {
                "fingerprint": fingerprint,
                "nickname": nickname,
                "node": self.get_node_info(fingerprint),
                "status": status,
                "address": parts[2].strip('"') if len(parts) == 3 else None,
            }
            connections.append(connection)
        return connections

    # --------------------------------------------------------------
    def signal(self, signal_name):
        """
        Send a signal to the Tor process.
        """
        valid_signals = [
            "RELOAD", "SHUTDOWN", "DUMP", "DEBUG", "HALT",
            "HUP", "INT", "USR1", "USR2", "TERM", "NEWNYM",
            "CLEARDNSCACHE", "HEARTBEAT", "ACTIVE", "DORMANT"
        ]
        if signal_name not in valid_signals:
            raise ValueError(f"Invalid signal: {signal_name}")
        return self.send_command(f"SIGNAL {signal_name}")

    def set_conf(self, **kwargs):
        """
        Change the value of one or more configuration variables.
        """
        command = "SETCONF " + " ".join(f"{key}={value}" for key, value in kwargs.items())
        return self.send_command(command)

    def reset_conf(self, *keys):
        """
        Reset configuration values to their defaults.
        """
        command = "RESETCONF " + " ".join(keys)
        return self.send_command(command)

    def get_conf(self, *keys):
        """
        Retrieve the values of one or more configuration variables.
        """
        command = "GETCONF " + " ".join(keys)
        response = self.send_command(command)
        conf = {}
        for line in response.splitlines():
            if line.startswith("250 "):
                key, _, value = line[4:].partition("=")
                conf[key] = value.strip()
        return conf

    def reload_config(self):
        """
        Reload the Tor configuration file.

        Returns:
            str: The response from Tor control.
        """
        return self.signal("RELOAD")

    def get_log(self, log_type="INFO"):
        """
        Retrieve logs from the Tor instance.

        Args:
            log_type (str): The type of logs to retrieve (e.g., "DEBUG", "INFO", "NOTICE").

        Returns:
            str: The logs from Tor.
        """
        valid_types = ["DEBUG", "INFO", "NOTICE", "WARN", "ERR"]
        if log_type not in valid_types:
            raise ValueError(f"Invalid log type: {log_type}")
        return self.send_command(f"GETINFO log/{log_type.lower()}")

    def redirect_stream(self, stream_id, address):
        """
        Redirect a stream to a specific address.

        Args:
            stream_id (str): The ID of the stream to redirect.
            address (str): The address to redirect the stream to.

        Returns:
            str: The response from Tor control.
        """
        return self.send_command(f"REDIRECTSTREAM {stream_id} {address}")

    def close_stream(self, stream_id, reason=None):
        """
        Close a specific stream.

        Args:
            stream_id (str): The ID of the stream to close.
            reason (str, optional): The reason for closing the stream.

        Returns:
            str: The response from Tor control.
        """
        command = f"CLOSESTREAM {stream_id}"
        if reason:
            command += f" REASON={reason}"
        return self.send_command(command)

