# G2S Emergency stop state
std_msgs/Header header

uint32[] emergency_stop_state                         # Emergency stop button request (0: Not activated; 1: Activated)
uint32[] emergency_stop_fault_state                   # Emergency stop button fault status (0: Normal; 1: Fault)