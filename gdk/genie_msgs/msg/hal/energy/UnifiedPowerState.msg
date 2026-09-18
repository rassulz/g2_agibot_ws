# G02 Chassis Power Status
std_msgs/Header header

uint8 battery_power_supply_button_fault_state        # Main power switch fault state (0: Normal; 1: Fault)
uint8 battery_power_supply_button_state              # Main power switch state (0: Off; 1: On)
uint8 battery_power_switch_power_state               # Battery main power output switch state (0: Off; 1: On)
uint8 power_48v_bus_power_on_fault_state             # 48V bus power-on fault state (0: No power-on fault occurred; 1: Power-on fault occurred)
uint32[] chassis_lidar_power_state                    # [0]: lidar1, front  [1]: lidar2, rear. LiDAR power supply state (0: Power off; 1: Power on)
uint32[] led_strip_power_state                        # Led strip power board state (0: Power off; 1: Power on) 
uint32[] chassis_output_power_state                   # [0]:output 1 [1]: output2. Chassis external power output state (0: Power off; 1: Power on)
uint8 chassis_power_board_power_state                # Chassis power board status (0: Low power mode; 1: Full power mode)
uint8 chassis_ultrasonic_radar_power_state           # Ultrasonic radar power supply state (0: Power off; 1: Power on)
uint32[] chassis_traction_motor_power_state           # [0]: left front, [1]: right front, [2]: mid rear. Traction motor power supply state (0: Power off; 1: Power on)
uint32[] chassis_steering_motor_power_state           # [0]: left front, [1]: right front, [2]: mid rear. Steering motor power supply state (0: Power off; 1: Power on)
uint32[] body_motor_power_state                       # [0]: waist, [1]: lift. Body motor power switch status (0: Power off; 1: Power on)
float32 chassis_power_board_temperature              # temperature of chassis power board
uint8 chassis_board_12v_output_fault_state           # Chassis power board 12V output fault state (0: No output fault occurred; 1: Output fault occurred)
uint8 chassis_board_5v_output_fault_state            # Chassis power board 5V output fault state (0: No output fault occurred; 1: Output fault occurred)
uint8 remote_exist                                   # Chassis remote controller existence flag (0: No remote; 1: Remote exists)
uint8 domain_controller_power_onoff_req              # Domain controller power switch on/off request (0: Power off; 1: Power on)
uint8 power_button_fault_state                       # Power switch fault status (0: Normal; 1: Fault)
uint8 head_interactive_board_power_state             # Head interactive board power switch status (0: Power off; 1: Power on)
uint32[] head_motor_power_state                       # [0]: pitch. Head motor power switch status (0: Power off; 1: Power on)
uint8 left_arm_power_state                           # Left arm motor power switch status (0: Power off; 1: Power on)
uint8 right_arm_power_state                          # Right arm motor power switch status (0: Power off; 1: Power on)
uint32[] head_motor_short_circuit_fault_state         # [0]: pitch. Head motor power supply short circuit fault (0: No motor short circuit occurred; 1: Motor short circuit occurred)
uint32[] body_motor_short_circuit_fault_state         # [0]: waist, [1]: lift. Body motor power supply short circuit fault (0: No motor short circuit occurred; 1: Motor short circuit occurred)
uint8 left_arm_motor_short_circuit_fault_state       # Left arm motor power supply short circuit fault (0: No motor short circuit occurred; 1: Motor short circuit occurred)
uint8 right_arm_motor_short_circuit_fault_state      # Right arm motor power supply short circuit fault (0: No motor short circuit occurred; 1: Motor short circuit occurred)
uint8 charge_plug_input_short_circuit_fault_state    # Charging plug short circuit fault status (0: No short circuit; 1: Short circuit occurred)
uint8 charge_plug_input_open_circuit_fault_state     # Charging plug reverse connection fault status (0: No reverse connection; 1: Reverse connection occurred)
uint8 charge_plug_insert_state                       # Charging plug insertion state (0: Charging plug not inserted; 1: Charging plug inserted)
float32 charge_plug_input_voltage                    # Charging plug input voltage (unit: V)
float32 charge_plug_input_current                    # Charging plug input current (unit: A)
uint8 emergency_stop_button_req                      # Emergency stop button request (0: Not activated; 1: Activated)
uint8 emergency_stop_button_fault_state              # Emergency stop button fault status (0: Normal; 1: Fault)
BatteryState[] battery_states

string power_board_software_version                  # Software version
string power_board_hardware_version                  # Hardware version
string power_board_serial_number                     # Serial number