package torcontrol

import (
	"bufio"
	"fmt"
	"net"
	"strings"
)

// Client represents the Tor control client.
type Client struct {
	conn   net.Conn
	reader *bufio.Reader
	writer *bufio.Writer
}

// NewClient initializes a new Tor control client.
func NewClient(host string, port int, password string) (*Client, error) {
	conn, err := net.Dial("tcp", fmt.Sprintf("%s:%d", host, port))
	if err != nil {
		return nil, fmt.Errorf("failed to connect to Tor control port: %w", err)
	}

	client := &Client{
		conn:   conn,
		reader: bufio.NewReader(conn),
		writer: bufio.NewWriter(conn),
	}

	// Authenticate with the Tor control port
	if err := client.authenticate(password); err != nil {
		return nil, fmt.Errorf("authentication failed: %w", err)
	}

	return client, nil
}

// Close closes the connection to the Tor control port.
func (c *Client) Close() error {
	return c.conn.Close()
}

// authenticate authenticates with the Tor control port.
func (c *Client) authenticate(password string) error {
	_, err := c.sendCommand(fmt.Sprintf("AUTHENTICATE \"%s\"", password))
	return err
}

// sendCommand sends a command to the Tor control port and returns the full response.
func (c *Client) sendCommand(command string) (string, error) {
	// Write the command to the socket
	if _, err := c.writer.WriteString(command + "\r\n"); err != nil {
		return "", fmt.Errorf("failed to send command: %w", err)
	}
	if err := c.writer.Flush(); err != nil {
		return "", fmt.Errorf("failed to flush command: %w", err)
	}

	// Download the full response until "250 OK" or a similar termination line
	var response strings.Builder
	for {
		line, err := c.reader.ReadString('\n')
		if err != nil {
			return "", fmt.Errorf("failed to read response: %w", err)
		}

		response.WriteString(line)

		// Stop reading if the response ends with "250 OK" or a period followed by "250 OK"
		if strings.HasPrefix(line, "250 ") || line == ".\r\n" {
			break
		}
	}

	return response.String(), nil
}
