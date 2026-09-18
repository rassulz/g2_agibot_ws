# Msg used for Cartesian impedance debug

std_msgs/Header header

string[] name

##################################################
#    Current left end and right end states       #
##################################################
geometry_msgs/Pose  left_end_pose_current      
geometry_msgs/Pose  right_end_pose_current     
geometry_msgs/Twist left_end_twist_current
geometry_msgs/Twist right_end_twist_current
geometry_msgs/Twist left_end_acceleration_current
geometry_msgs/Twist right_end_acceleration_current

##################################################
#    Received left end and right end commands    #
##################################################
geometry_msgs/Pose  left_end_pose_cmd      
geometry_msgs/Pose  right_end_pose_cmd     
geometry_msgs/Twist left_end_twist_cmd
geometry_msgs/Twist right_end_twist_cmd
geometry_msgs/Twist left_end_acceleration_cmd
geometry_msgs/Twist right_end_acceleration_cmd

##################################################
#                 Control error                  #
##################################################
float64[] cart_pose_error
float64[] cart_vel_error

##############################################################
#  Control parameters (Transformed into 1D array, row first) #
##############################################################
float64[] stiffness_matrix
float64[] damping_matrix
float64[] integral_gain
uint32[]  damping_method   # 0: CONSTANT, 1: DIAGONAL, 2: DIAGONAL_ADVANCED
uint32[]  control_group    # 0: DUAL_ARM, 1: LEFT_ARM, 2: RIGHT_ARM

##################################################
#             Control torque commands            #
##################################################
float64[] proportional_part
float64[] damping_part
float64[] acc_compensation_part
float64[] integral_part
float64[] cartesian_impedance_force
float64[] cartesian_impedance_torque
float64[] nonlinear_effects

##################################################
#                 Joint Feedback                 #
##################################################
float64[] joint_position
float64[] joint_velocity
float64[] joint_effort
float64[] motor_current
uint32[] control_mode
