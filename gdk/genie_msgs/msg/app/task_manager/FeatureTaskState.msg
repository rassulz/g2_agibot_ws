std_msgs/Header header

# 与 TaskCommand 一致的任务标识
string task_id
string feature

# 任务生命周期/行为树式状态
uint8 STATE_UNKNOWN=0
uint8 STATE_PENDING=1      # 已接收等待调度/资源
uint8 STATE_ACCEPTED=2     # 已受理，准备执行（装配 BT/规划中）
uint8 STATE_RUNNING=3      # 执行中（BT: RUNNING）
uint8 STATE_SUCCEEDED=4    # 成功完成（BT: SUCCESS）
uint8 STATE_FAILED=5       # 失败结束（BT: FAILURE）
uint8 STATE_CANCELED=6     # 已取消
uint8 STATE_ABORTED=7      # 主动/被动中止（一般较失败更“硬”）
uint8 STATE_PAUSED=8       # 暂停中
uint8 STATE_TIMEOUT=9      # 超时结束
uint8 task_state

# 进度 0.0~1.0（未知填 -1.0）
float32 progress

string error_msg

string sub_task
uint8 sub_task_state

string data_json

builtin_interfaces/Duration run_time   # 本次运行时长