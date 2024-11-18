package torcontrol

import "strings"

// Circuit represents a Tor circuit.
type Circuit struct {
	ID     string
	Status string
	Path   string
}

// CircuitEvent represents a circuit event.
type CircuitEvent struct {
	ID     string
	Status string
	Path   []string
}

// readAsyncEvent reads an asynchronous event from the Tor control port.
func (c *Client) readAsyncEvent() (string, error) {
	response, err := c.reader.ReadString('\n')
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(response), nil
}

// WatchCircuits monitors circuit events in real-time.
func (c *Client) WatchCircuits() <-chan CircuitEvent {
	ch := make(chan CircuitEvent)
	go func() {
		defer close(ch)
		for {
			response, err := c.readAsyncEvent()
			if err != nil {
				return
			}
			if strings.HasPrefix(response, "650 CIRC") {
				parts := strings.Fields(response[8:])
				if len(parts) < 2 {
					continue
				}
				event := CircuitEvent{
					ID:     parts[0],
					Status: parts[1],
				}
				if len(parts) > 2 {
					event.Path = strings.Split(parts[2], ",")
				}
				ch <- event
			}
		}
	}()
	return ch
}
