# G02 Chassis Power Control
std_msgs/Header header

uint8 chassis_power_board_power_ctrl_req             # Chassis power board sleep/wake control (0: Request low power mode; 1: Request full power mode)
uint32[] chassis_traction_motor_power_ctrl_req        # [0]: left front, [1]: right front, [2]: mid rear. Traction motor power control (0: Request to turn off power; 1: Request to turn on power)
uint32[] chassis_steering_motor_power_ctrl_req        # [0]: left front, [1]: right front, [2]: mid rear. Steering motor power control (0: Request to turn off power; 1: Request to turn on power)
uint32[] chassis_lidar_power_ctrl_req                 # [0]: lidar1, front  [1]: lidar2, rear. LiDAR power control (0: Request to turn off power; 1: Request to turn on power)
uint32[] body_motor_power_ctrl_req                    # [0]: waist [1]: lift. Body motor power control (0: Request to turn off power; 1: Request to turn on power)
uint8 chassis_ultrasonic_radar_power_ctrl_req        # Ultrasonic radar power control (0: Request to turn off power; 1: Request to turn on power)
uint32[] chassis_output_power_ctrl_req                # [0]:output 1. # External power output control (0: Request to turn off power; 1: Request to turn on power)
uint8 charging_plug_power_ctrl_req                   # Charging plug power control (0: Request to turn off power; 1: Request to turn on power)
uint8 battery_power_switch_power_ctrl_req            # Battery main power switch control (0: Request to turn off; 1: Request to turn on)
uint32[] battery_bms_switch_power_ctrl_req            # Battery  BMS switch control (0: Request to turn off BMS; 1: Request to turn on BMS)
float32 charger_max_charging_current_ctrl_req        # Charger maximum charging current control request (Unit: A, Precision: 0.1A, Range: -44.0A to 44.0A)
float32 charger_max_charging_voltage_ctrl_req        # Charger maximum charging voltage control request (Unit: V, Precision: 0.1V, Range: -60.0V to 60.0V)
uint32[] led_strip_power_ctrl_req                     # Led strip power control (0: Request to turn off power; 1: Request to turn on power)
uint8 head_interactive_board_power_ctrl_req          # Head interactive board power control (0: Request to turn off power; 1: Request to turn on power)
uint32[] head_motor_power_ctrl_req                    # [0]: head pitch
uint8 left_arm_power_ctrl_req                        # Left arm motor power control (0: Request to turn off power; 1: Request to turn on power)
uint8 right_arm_power_ctrl_req                       # Right arm motor power control (0: Request to turn off power; 1: Request to turn on power)