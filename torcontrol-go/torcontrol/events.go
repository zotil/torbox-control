package torcontrol

import (
	"fmt"
	"strings"
	"time"
)

// BandwidthEvent represents a bandwidth usage event.
type BandwidthEvent struct {
	Time    string
	Read    string
	Written string
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
				// time now YYYY-MM-DD HH:MM:SS
				timeNow := time.Now().Format("2006-01-02 15:04:05")
				ch <- BandwidthEvent{
					Time:    timeNow,
					Read:    parts[0],
					Written: parts[1],
				}
			}
		}
	}()
	return ch
}
