std_msgs/Header header

# 路径点序列（只包含位置，无速度/加速度/时间）
# 用于 PlanPath 服务返回的路径数据
PathPoint[] points

# 元信息
uint32 group_bits              # 关节组位掩码
string[] joint_names           # 关节名称列表

# 约束信息（供后续 TOPP/时间参数化使用）
float64[] velocity_limits      # 速度限制 [rad/s]
float64[] acceleration_limits  # 加速度限制 [rad/s^2]
