float64 arm_angle                          # 臂角，单位rad
# 全局IK初值使用
string[] reference_joint_names             # 参考角度名称，用于IK初值
float64[] reference_joint_positions        # 参考角度值，用于IK初值
# 参考坐标系代价
string[] reference_frame_names             # 参考frame名称，用于求解IK代价
geometry_msgs/Pose[] reference_frame_poses # 参考frame位姿，用于求解IK代价
float64[] reference_frame_weights