# Msg used for Joint impedance debug

std_msgs/Header header

string[] name

##################################################
#    Current left arm and right arm states       #
##################################################
float64[] left_arm_angle_current      
float64[] right_arm_angle_current     
float64[] left_arm_velocity_current
float64[] right_arm_velocity_current
float64[] left_arm_acceleration_current
float64[] right_arm_acceleration_current

##################################################
#    Received left arm and right arm commands    #
##################################################
float64[] left_arm_angle_cmd      
float64[] right_arm_angle_cmd     
float64[] left_arm_velocity_cmd
float64[] right_arm_velocity_cmd
float64[] left_arm_acceleration_cmd
float64[] right_arm_acceleration_cmd

##################################################
#                 Control error                  #
##################################################
float64[] joint_pos_error
float64[] joint_vel_error

##############################################################
#  Control parameters (Transformed into 1D array, row first) #
##############################################################
float64[] stiffness_matrix
float64[] damping_matrix
float64[] integral_gain
uint32[]  control_group    # 0: DUAL_ARM, 1: LEFT_ARM, 2: RIGHT_ARM

##################################################
#             Control torque commands            #
##################################################
float64[] total_goal_velocity
float64[] damping_part
float64[] acc_compensation_part
float64[] integral_part
float64[] joint_impedance_torque
float64[] nonlinear_effects
