std_msgs/Header header

############################################################
# 控制来源（输入源）
############################################################
uint8 INPUT_AUTO    = 0    # 自动（系统/任务管理）
uint8 INPUT_TELEOP  = 1    # 人工遥操作（手柄/VR/MoCap）
uint8 INPUT_HMI     = 2    # 本体HMI/平板
uint8 INPUT_END_BTN = 3    # 末端按钮
uint8 INPUT_VLA     = 4    # 大模型/VLA
uint8 INPUT_RL      = 5    # 强化学习
uint8 INPUT_GDK     = 6    # SDK/外部API
uint8 input_source

############################################################
# 控制目标（控制哪部分）
############################################################
uint8 TARGET_ARMS      = 0 # 双臂（若提供左右都有效的目标）
uint8 TARGET_LEFT_ARM  = 1
uint8 TARGET_RIGHT_ARM = 2
uint8 target

############################################################
# 控制模式
############################################################
uint8 CTRL_AUTO_POS            = 0  # auto 位控（由上层决定细节）
uint8 CTRL_JOINT_POSITION      = 1  # 关节位控（PD/轨迹）
uint8 CTRL_CARTESIAN_IMPEDANCE = 2  # 笛卡尔阻抗
uint8 CTRL_JOINT_IMPEDANCE     = 3  # 关节阻抗
uint8 CTRL_GRAVITY_COMP_TEACH  = 4  # 拖拽示教（重力补偿/低刚度）
uint8 control_mode

############################################################
# 安全模式
############################################################
uint8 SAFE_NORMAL   = 0  # 正常
uint8 SAFE_REDUCED  = 1  # 降速/受限
uint8 SAFE_STOP     = 2  # 安全停
uint8 safe_mode

uint8  priority      # 可选：优先级（0-255，数值越大越高） 

string uuid          
string detail       