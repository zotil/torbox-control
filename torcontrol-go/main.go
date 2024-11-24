package main

import (
	"log"
	"torcontrol-go/torcontrol"
)

func main() {
	// Initialize the Tor Control Client
	client, err := torcontrol.NewClient("192.168.44.1", 9051, "CHANGE-IT")
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
	//err = client.SetEvents([]string{"BW"})
	//if err != nil {
	//	log.Fatalf("Failed to enable bandwidth events: %v", err)
	//}
	//fmt.Println("Monitoring bandwidth events...")
	//for event := range client.WatchBandwidth() {
	//	fmt.Printf("Time: %s, Read: %s bytes, Written: %s bytes\n", event.Time, event.Read, event.Written)
	//}

	// Get circuits and list them
	circuits, err := client.GetCircuits()
	if err != nil {
		log.Fatalf("Failed to get circuits: %v", err)
	}
	for _, circuit := range circuits {
		log.Printf("ID: %s, Status: %s, Path: %s\n", circuit.ID, circuit.Status, circuit.Path)
	}

}
