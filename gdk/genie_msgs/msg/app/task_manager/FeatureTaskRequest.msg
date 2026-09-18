std_msgs/Header header

# 任务唯一 ID（由上层生成并保持一致）
string task_id

# 功能名 / 特性名，例如 "auto_docking"
string feature

# 任务来源 例如 'hmi'  'speech' 'gdk' 
string task_source

# 控制指令类型（仿照行为树与任务管理常见动作）
uint8 CMD_UNKNOWN=0
uint8 CMD_START=1         # 触发/开始任务
uint8 CMD_UPDATE=2        # 运行中更新参数（例如目标点变更）
uint8 CMD_CANCEL=3        # 请求取消
uint8 CMD_PAUSE=4         # 暂停
uint8 CMD_RESUME=5        # 恢复
uint8 CMD_RETRY=6         # 失败后重试一次（或由上层策略决定）
uint8 CMD_ABORT=7         # 强制中止（立即停/回收资源）

uint8 command

# （可选）期望的截止时间、超时等，可不填
builtin_interfaces/Duration timeout

# （可选）优先级，数值越大优先级越高；未使用可填 0
int32 priority

# 用 JSON 串封装复杂结构（例如目标位姿、路径约束等）
string data_json

string uuid
string detail
