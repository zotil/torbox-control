package torcontrol

import (
	"fmt"
	"strings"
)

// GetCircuits retrieves the list of active circuits.
func (c *Client) GetCircuits() ([]Circuit, error) {
	response, err := c.sendCommand("GETINFO circuit-status")
	if err != nil {
		return nil, err
	}

	fmt.Println("Raw Response:", response) // Debug the raw response

	var circuits []Circuit
	lines := strings.Split(response, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "." || strings.HasPrefix(line, "250 ") || strings.HasPrefix(line, "250+") {
			continue
		}

		parts := strings.Fields(line)
		if len(parts) < 3 {
			continue
		}

		circuit := Circuit{
			ID:     parts[0],
			Status: parts[1],
			Path:   parts[2],
		}
		circuits = append(circuits, circuit)
	}
	return circuits, nil
}

// SetEvents configures which events to monitor.
func (c *Client) SetEvents(events []string) error {
	_, err := c.sendCommand("SETEVENTS " + strings.Join(events, " "))
	return err
}

// SetConf modifies the Tor configuration.
func (c *Client) SetConf(config map[string]string) error {
	var settings []string
	for key, value := range config {
		settings = append(settings, fmt.Sprintf("%s=%s", key, value))
	}
	command := "SETCONF " + strings.Join(settings, " ")
	_, err := c.sendCommand(command)
	return err
}
