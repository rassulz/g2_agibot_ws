# G02 Battery Status

uint8  battery_bms_charge_or_discharge             # Battery BMS charge/discharge status (0: Discharging; 1: Charging)

float32 battery_bms_output_voltage                 # Battery BMS output voltage (unit: V)

float32 battery_bms_output_current                 # Battery BMS output current (unit: A)

float32 battery_bms_charge_current                 # Battery BMS input (charging) current (unit: A)

float32 battery_bms_temperature                    # Battery BMS temperature (unit: °C)

float32 battery_bms_soc                            # Battery BMS State of Charge (SOC) (unit: percentage 0%-100%)

uint8  battery_bms_soh                             # Battery BMS State of Health (SOH) (unit: percentage 0%-100%)

uint8  battery_bms_short_circuit_fault_state       # Battery BMS short circuit fault status (0: No short circuit; 1: Short circuit occurred)

uint8  battery_bms_open_circuit_fault_state        # Battery BMS open circuit fault status (0: No open circuit; 1: Open circuit occurred)

uint32  battery_bms_other_fault_state              # Battery BMS other fault status (0: No fault; 1-4294967295: Fault code)

float32 battery_outside_output_voltage             # Battery external output voltage (unit: V)

uint8  battery_outside_connection                  # Battery external plug status (0: Plug connected; 1: Plug disconnected)

uint8  battery_outside_open_circuit_fault_state    # Battery external open circuit fault status (0: Plug connected; 1: Plug disconnected)

uint8 battery_bms_switch_power_state               # Battery BMS switch state (0: Off; 1: On)

uint8 battery_unlock_state                         # Battery electronic unlock state (0: Locked; 1: Unlocked)

uint8 battery_input_fault_state                    # Battery input fault state (0: No input fault occurred; 1: Input fault occurred)

uint8 battery_charge_mos_power_state               # Battery charging MOS switch state (0: Charging cut off; 1: Charging enabled)

