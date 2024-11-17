from tor_control import TORBOX_IP_MINI, TOR_CONTROL_PASSWORD, TorControl, TORBOX_IP_WIFI

# Create a new TorBoxControl instance
tor_control = TorControl(torbox_ip=TORBOX_IP_WIFI)
tor_control.authenticate(TOR_CONTROL_PASSWORD)

# Console loop
while True:
    try:
        # wait user input
        command = input("torbox@control > ")
        if command == "exit":
            break
        # send command to tor control
        try:
            response = tor_control.send_command(command)
            print(response)
        except Exception as e:
            print("[x] Command failed: ", e)

    except KeyboardInterrupt:
        break
