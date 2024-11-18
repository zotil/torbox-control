package torcontrol

import (
	"fmt"
	"strings"
)

// Node represents a Tor node.
type Node struct {
	Fingerprint string
	IP          string
	Port        int
	Flags       []string
}

func (c *Client) GetNodeInfo(fingerprint string) (*Node, error) {
	command := fmt.Sprintf("GETINFO ns/id/%s", fingerprint)
	response, err := c.sendCommand(command)
	if err != nil {
		return nil, err
	}

	var node Node
	lines := strings.Split(response, "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if strings.HasPrefix(line, "r ") {
			parts := strings.Fields(line)
			if len(parts) < 8 {
				continue
			}
			node = Node{
				Fingerprint: fingerprint,
				IP:          parts[6],
				Port:        atoi(parts[7]),
			}
		}
		if strings.HasPrefix(line, "s ") {
			node.Flags = strings.Fields(line[2:])
		}
	}
	return &node, nil
}
