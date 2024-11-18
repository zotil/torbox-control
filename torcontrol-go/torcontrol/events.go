package torcontrol

import (
	"fmt"
	"strings"
)

// BandwidthEvent represents a bandwidth usage event.
type BandwidthEvent struct {
	Time     string
	Download string
	Upload   string
}

// WatchBandwidth monitors bandwidth events in real-time.
func (c *Client) WatchBandwidth() <-chan BandwidthEvent {
	ch := make(chan BandwidthEvent)
	go func() {
		defer close(ch)
		for {
			response, err := c.readAsyncEvent()
			if err != nil {
				fmt.Println("Error reading bandwidth event:", err)
				return
			}

			if strings.HasPrefix(response, "650 BW") {
				parts := strings.Fields(response[7:])
				if len(parts) > 2 {
					continue
				}
				ch <- BandwidthEvent{
					Download: parts[0],
					Upload:   parts[1],
				}
			}
		}
	}()
	return ch
}
