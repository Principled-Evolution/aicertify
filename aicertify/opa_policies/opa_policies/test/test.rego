package opa_policies.test

import rego.v1

# Default rules
default allow := false

# Define rules
allow if input.test == true

default example_value := "failure"

example_value := "success" if input.test == true

# Has something rule
has_something if input.something

check_condition if {
	x := 10
	x > 5
}
