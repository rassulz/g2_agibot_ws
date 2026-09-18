# HMI 笛卡尔规划请求，与 MotionControlService.HMICartesianPlan 配套

uint8 CARTESIAN_LINEAR = 0
uint8 CARTESIAN_RRT = 1
uint8 type

CartesianTarget[] targets

# 运动时长缩放 0.1~1.0，1.0 最快；建议默认 0.5
float64 duration_scale
# 加速度缩放 0.1~1.0，1.0 最大；建议默认 0.5
float64 acceleration_scale

bool enable_waist_passive

string uuid
