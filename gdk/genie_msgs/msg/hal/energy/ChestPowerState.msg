# G02 Upper Body Power Status
std_msgs/Header header

uint8 power_onoff_req                               # Power switch on/off request (0: Power off; 1: Power on)
uint8 emergency_stop_button_req                     # Emergency stop button request (0: Not activated; 1: Activated)
uint8 power_button_fault_state                      # Power switch fault status (0: Normal; 1: Fault)
uint8 emergency_stop_button_fault_state             # Emergency stop button fault status (0: Normal; 1: Fault)
uint8 power_full_low_req                            # Power mode request (0: Full power mode; 1: Low power mode)
uint8 chest_power_board_power_state                 # Chest power board power status (0: Low power mode; 1: Full power mode)
uint8 domain_controller_power_state                 # Domain controller power switch status (0: Power off; 1: Power on)
uint8 head_interactive_board_power_state            # Head interactive board power switch status (0: Power off; 1: Power on)
uint8 curved_screen_power_state                     # Curved screen power switch status (0: Power off; 1: Power on)

uint8 head_yaw_motor_power_state                    # Head yaw motor power switch status (0: Power off; 1: Power on)
uint8 head_pitch_motor_power_state                  # Head pitch motor power switch status (0: Power off; 1: Power on)
uint8 head_roll_motor_power_state                   # Head roll motor power switch status (0: Power off; 1: Power on)
uint8 waist_yaw_motor_power_state                   # Waist yaw motor power switch status (0: Power off; 1: Power on)
uint8 head_motor_short_circuit_fault_state          # Head motor power supply short circuit fault (0: No motor short circuit occurred; 1: Motor short circuit occurred)
uint8 waist_pitch_motor_power_state                 # Waist pitch motor power switch status (0: Power off; 1: Power on)
uint8 leg_bending1_motor_power_state                # Leg bending motor #1 power switch status (0: Power off; 1: Power on)
uint8 leg_bending2_motor_power_state                # Leg bending motor #2 power switch status (0: Power off; 1: Power on)
uint8 leg_bending3_motor_power_state                # Leg bending motor #3 power switch status (0: Power off; 1: Power on)
uint8 waist_motor_short_circuit_fault_state         # Waist motor power supply short circuit fault (0: No motor short circuit occurred; 1: Motor short circuit occurred)

uint8 left_arm_power_state                          # Left arm motor power switch status (0: Power off; 1: Power on)
uint8 left_arm_motor_short_circuit_fault_state      # Left arm motor power supply short circuit fault (0: No motor short circuit occurred; 1: Motor short circuit occurred)
uint8 left_arm_break_enable_state                   # Left arm motor brake enable status (0: Brake enable control off; 1: Brake enable control on)
uint8 right_arm_power_state                         # Right arm motor power switch status (0: Power off; 1: Power on)
uint8 right_arm_motor_short_circuit_fault_state     # Right arm motor power supply short circuit fault (0: No motor short circuit occurred; 1: Motor short circuit occurred)
uint8 right_arm_break_enable_state                  # Right arm motor brake enable status (0: Brake enable control off; 1: Brake enable control on)

uint8 fan_power_state                               # Fan power switch status (0: Power off; 1: Power on)
uint8 chest_power_board_fan_fault_state             # Chest power board internal fan fault status (0: Status normal; 1: Status abnormal)
uint8 body_fan1_fault_state                         # Body fan #1 fault status (0: Status normal; 1: Status abnormal)
uint8 body_fan2_fault_state                         # Body fan #2 fault status (0: Status normal; 1: Status abnormal)
uint8 body_fan3_fault_state                         # Body fan #3 fault status (0: Status normal; 1: Status abnormal)
uint8 body_fan4_fault_state                         # Body fan #4 fault status (0: Status normal; 1: Status abnormal)

uint8 upper_body_led_strip_power_state              # Upper body LED strip power switch status (0: Power off; 1: Power on)
uint8 poe_power_state                               # POE power switch status (0: Power off; 1: Power on)
uint8 ipad_power_state                              # iPad power switch status (0: Power off; 1: Power on)
uint8 chest_reserved_lidar_power_state              # Reserved LiDAR power switch status (0: Request to power off; 1: Request to power on)
float32 chest_power_board_temperature               # Temperature of chest power board (-40°C to 87.5°C, resolution 0.5°C)

uint32 chest_power_board_fault_state                # Chest power board fault code (0: No fault; 1-4294967295: Fault code)
string power_board_software_version                 # Software version
string power_board_hardware_version                 # Hardware version
string power_board_serial_number                    # Serial number

