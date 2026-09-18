# G02 Chassis Power Status
std_msgs/Header header

uint8 battery_power_supply_button_state              # Battery main power switch state (0: Off; 1: On)
uint8 emergency_stop_pedal_state                     # Emergency stop pedal state (0: Not activated; 1: Activated)
uint8 battery_power_supply_button_fault_state        # Battery main power switch fault state (0: Normal; 1: Fault)
uint8 emergency_stop_pedal_fault_state               # Emergency stop pedal fault state (0: Normal; 1: Fault)
uint8 chassis_power_board_power_state                # Chassis power board status (0: Low power mode; 1: Full power mode)

uint8 chassis_left_traction_motor_power_state        # Left traction motor power supply state (0: Power off; 1: Power on)
uint8 chassis_right_traction_motor_power_state       # Right traction motor power supply state (0: Power off; 1: Power on)
uint8 chassis_left_steering_motor_power_state        # Left steering motor power supply state (0: Power off; 1: Power on)
uint8 chassis_right_steering_motor_power_state       # Right steering motor power supply state (0: Power off; 1: Power on)

uint8 chassis_lidar1_power_state                     # LiDAR #1 power supply state (0: Power off; 1: Power on)
uint8 chassis_lidar2_power_state                     # LiDAR #2 power supply state (0: Power off; 1: Power on)
uint8 chassis_ultrasonic_radar_power_state           # Ultrasonic radar power supply state (0: Power off; 1: Power on)
uint8 chassis_tof_camera_power_state                 # TOF camera power supply state (0: Power off; 1: Power on)
uint8 chassis_ethernet_switch_power_state            # Ethernet switch power supply state (0: Power off; 1: Power on)

uint8 chassis_output_power_state                     # Chassis external power output state (0: Power off; 1: Power on)
uint8 battery_power_switch_power_state               # Battery main power output switch state (0: Off; 1: On)

BatteryState[] battery_states

uint8 charge_plug_insert_state                       # Charging plug insertion state (0: Charging plug not inserted; 1: Charging plug inserted)
float32 charge_plug_input_voltage                    # Charging plug input voltage (unit: V)
float32 charge_plug_input_current                    # Charging plug input current (unit: A)
uint8 charge_plug_input_short_circuit_fault_state    # Charging plug short circuit fault status (0: No short circuit; 1: Short circuit occurred)
uint8 charge_plug_input_open_circuit_fault_state     # Charging plug reverse connection fault status (0: No reverse connection; 1: Reverse connection occurred)

uint8 chassis_led_strip_power_state                  # Chassis led strip power board state (0: Power off; 1: Power on) 
float32 chassis_power_board_temperature              # temperature of chassis power board

uint8 power_48v_bus_power_on_fault_state             # 48V bus power-on fault state (0: No power-on fault occurred; 1: Power-on fault occurred)
uint8 power_poe_bus_power_on_fault_state             # POE bus power-on fault state (0: No power-on fault occurred; 1: Power-on fault occurred)
uint8 chassis_board_12v_output_fault_state           # Chassis power board 12V output fault state (0: No output fault occurred; 1: Output fault occurred)
uint8 chassis_board_5v_output_fault_state            # Chassis power board 5V output fault state (0: No output fault occurred; 1: Output fault occurred)

uint32 chassis_power_board_fault_state               # Chassis power board fault code (0: No fault; 1-4294967295: Fault code)

string power_board_software_version                  # Software version
string power_board_hardware_version                  # Hardware version
string power_board_serial_number                     # Serial number