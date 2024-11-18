package torcontrol

import "strconv"

// atoi converts a string to an integer with error handling.
func atoi(s string) int {
	i, _ := strconv.Atoi(s)
	return i
}
