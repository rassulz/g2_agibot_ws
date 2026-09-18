# The command of each joint (revolute or prismatic) is defined by:
#  * the control mode (csp 0, cst 1, mit 2)
#  * the position of the joint (rad or m),
#  * the velocity of the joint (rad/s or m/s),
#  * the effort that is applied in the joint (Nm or N),

std_msgs/Header header

string[] name
uint32[] mode
float64[] position
float64[] velocity
float64[] effort

float64[] kp
float64[] kd

float64[] inertia_ff
float64[] torque_base