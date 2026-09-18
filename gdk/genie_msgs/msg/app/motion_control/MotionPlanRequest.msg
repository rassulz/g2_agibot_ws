std_msgs/Header header # frame id 无用, timestamp发送时间

# ======================= 发出控制源 ===================================
uint8 INPUT_VR = 51
uint8 INPUT_MOCAP = 52
uint8 INPUT_HMI = 53
uint8 INPUT_GDK = 54
uint8 input_type

uint8 PLAN_JOINT_SPACE = 0
uint8 PLAN_CARTESIAN_SPACE = 1
uint8 INTERP_JOINT_SPACE = 2
uint8 INTERP_CARTESIAN_SPACE = 3
uint8 type

# ======================== 控制组目标 ===================================
# 用于确定IK求解以及规划的自由度
# 注意：group_id在不同group内不能一样
PlanningTarget[] targets

# ======================== IK与规划过程中硬约束 ===================================
# 用于路径规划以及轨迹优化的约束施加（暂时只是空间约束）
# 注意：给定的过程约束不能与控制组目标约束出现违背
PlanningConstraints constraints

# ======================== 时间参数化 ===================================
uint8 SCALED_TIME = 0
uint8 ACCURATE_TIME = 1
uint8 time_parametization
# SCALED_TIME: 时间范围 0-1  1最快
# ACCURATE_TIME: 准确时间， 需要判断是否超时
float64 time

# 控制最大加速度比例（0~1）
float64 acc

# ======================== 动态求解参数 ===================================
float64 timeout
uint64 seed

string root_log_path
uint8 LOG_LEVEL_VERBOSE = 0
uint8 LOG_LEVEL_DEBUG = 1
uint8 LOG_LEVEL_RELEASE = 2
uint8 LOG_LEVEL_NONE = 3
uint8 log_level

bool enable_env_collision
bool enable_self_collision
bool enable_com_check
bool enable_joint_limit

string uuid

# true: 只求解IK，不执行轨迹；将终态关节角序列化到 CommonResponse.reason 返回
bool ik_only