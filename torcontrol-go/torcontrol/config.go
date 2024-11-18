package torcontrol

import (
	"fmt"
)

// Config holds the Tor control client configuration.
type Config struct {
	Host     string
	Port     int
	Password string
}

// Address returns the full address of the Tor control port.
func (c *Config) Address() string {
	return fmt.Sprintf("%s:%d", c.Host, c.Port)
}
