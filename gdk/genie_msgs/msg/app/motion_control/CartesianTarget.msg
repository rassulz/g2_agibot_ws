# HMI 笛卡尔单段目标，与 HMICartesianRequest 配套

uint32 group_id

# 末端 frame（与 arm_l_end_link / arm_r_end_link 对应）
uint8 LEFT_ARM_END = 0
uint8 RIGHT_ARM_END = 1
uint8 target_frame

# 基座 frame
uint8 BASE_LINK = 0
uint8 base_frame

geometry_msgs/Pose target_pose

uint8 ABSOLUTE = 0
uint8 RELATIVE = 1
uint8 pose_mode
