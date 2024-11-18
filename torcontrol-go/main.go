package main

import (
	"fmt"
	"log"
	"torcontrol-go/torcontrol"
)

func main() {
	// Initialize the Tor Control Client
	client, err := torcontrol.NewClient("192.168.42.1", 9051, "CHANGE-IT")
	if err != nil {
		log.Fatalf("Failed to connect to Tor: %v", err)
	}
	defer func(client *torcontrol.Client) {
		err := client.Close()
		if err != nil {
			log.Fatalf("Failed to close connection to Tor: %v", err)
		}
	}(client)

	// Example: Monitor bandwidth events
	err = client.SetEvents([]string{"BW"})
	if err != nil {
		log.Fatalf("Failed to enable bandwidth events: %v", err)
	}
	fmt.Println("Monitoring bandwidth events...")
	for event := range client.WatchBandwidth() {
		fmt.Printf("Download: %s bytes, Upload: %s bytes\n", event.Download, event.Upload)
	}
}
