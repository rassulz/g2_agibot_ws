builtin_interfaces/Time stamp

# Task logic name (optional)
string skill_name

# Command type enumeration
uint8 START   = 0    # Start task
uint8 CANCEL  = 1    # Cancel current task
uint8 PAUSE   = 2    # Pause execution
uint8 RESUME  = 3    # Resume from pause
uint8 SWITCH  = 4    # Switch to new task
uint8 RESET   = 5    # Reset task tree (clear state)

# Command type
uint8 command

# Command source, e.g. 'hmi' 'speech' 'gdk' 'api'
string command_source

# Extended field: additional parameters passed as JSON string, e.g. {"speed":1.0, "target":"poseA"}
string params_json

# Unique identifier (UUID)
string uuid

# Detailed information or remarks
string detail