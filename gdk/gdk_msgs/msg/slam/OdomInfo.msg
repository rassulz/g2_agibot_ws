std_msgs/Header     header
string child_frame_id

geometry_msgs/PoseWithCovariance pose       # 六自由度的位姿
geometry_msgs/TwistWithCovariance twist     


bool is_stationary                          # 是否静止, 0：没有静止，1：静止
bool is_sliping                             # 是否正在打滑, 0:没有打滑，1：正在打滑
int32 loc_confidence                        # 定位置信度, 1~100, 数值越大置信度越高
int32 loc_state                             # 定位状态, 0：定位成功，1：定位丢失
geometry_msgs/Vector3 velocity              # 在世界系下的速度
geometry_msgs/Vector3 velocity_body         # 在body系下的速度
geometry_msgs/Vector3 acceleration          # 加速度
geometry_msgs/Vector3 ang_vel               # 角速度
geometry_msgs/Vector3 orientation_euler     # 姿态（欧拉角），单位弧度