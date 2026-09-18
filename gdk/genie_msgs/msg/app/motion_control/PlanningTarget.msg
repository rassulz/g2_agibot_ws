# 控制组Group序号
uint8 GROUP_HEAD_YAW = 0
uint8 GROUP_HEAD_PITCH = 1
uint8 GROUP_LEFT_ARM = 2
uint8 GROUP_RIGHT_ARM = 3
uint8 GROUP_LEFT_TOOL = 4 # 手或夹爪，mc根据配置
uint8 GROUP_RIGHT_TOOL = 5 # 手或夹爪，mc根据配置
uint8 GROUP_WAIST_LIFT = 6
uint8 GROUP_WAIST_PITCH = 7
uint8 GROUP_CHASSIS = 8
uint8 GROUP_HEAD_ROLL = 9
uint8 GROUP_WAIST = 10
uint8 group_id  #控制组序号

# 目标类型
uint8 POSE = 0
uint8 JOINT = 1
uint8 PASSIVE = 2
uint8 target_type

# ===================== 目标类型 0: 末端位姿 =============================
string target_frame                  # 目标末端的link名称(必须定义在该控制组内)
string base_frame                    # 目标末端控制位姿的base frame
geometry_msgs/Pose target_pose       # 目标末端控制位姿
float64[] target_velocity            # 目标末端控制速度
# 非全自由度位姿（TODO）
# --------------- IK求解相关参数 -----------------
IKSolverParameters ik_parameters

# ===================== 目标类型 1: 关节角 =============================
string[] target_joint_names # 目标角度名称(必须定义在该控制组内)
float64[] target_joint_positions # 目标角度值
float64[] target_joint_velocity  # 目标关节速度值
