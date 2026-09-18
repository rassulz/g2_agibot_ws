# TaskState.msg

# 任务状态枚举
# 0: idle, 1: running, 2: success, 3: failed
uint8 TASK_STATE_IDLE = 0
uint8 TASK_STATE_STARTING = 1
uint8 TASK_STATE_RUNNING = 2
uint8 TASK_STATE_PAUSING = 3
uint8 TASK_STATE_PAUSED = 4
uint8 TASK_STATE_RESUMING = 5
uint8 TASK_STATE_CANCELING = 6
uint8 TASK_STATE_CANCELED = 7
uint8 TASK_STATE_FAIL = 8
uint8 TASK_STATE_SUCCESS = 9
uint8 state

# 任务类型枚举
uint8 TASK_TYPE_IDLE = 0                # Idle task, no operation in progress
uint8 TASK_TYPE_NORMAL_NAVIGATION = 1   # Normal navigation task
uint8 TASK_TYPE_HIGH_PRECISION_NAVIGATION = 2  # High precision task
uint8 TASK_TYPE_REMOTE_CONTROL = 3      # Remote control task
uint8 TASK_TYPE_RELATIVE_MOVE = 4       # Relative move task
uint8 TASK_TYPE_PATH_FOLLOW_NAVIGATION = 5  # Path follow navigation task
uint8 type

# 风险等级枚举
uint8 RISK_LEVEL_NO_OBSTACLE = 0       # Level 0 No obstacle
uint8 RISK_LEVEL_FAR_WARNING = 1       # Level 1 Far-distance warning
uint8 RISK_LEVEL_NEAR_AVOIDANCE = 2    # Level 2 Near-distance avoidance
uint8 RISK_LEVEL_EMERGENCY_BRAKING = 3 # Level 3 Emergency braking
uint8 RISK_LEVEL_CROWD_CONGESTION = 4  # Level 4 Crowd congestion
uint8 level

# Unique identifier for the task
uint32 id

# Optional message providing additional information about the task state
string message

# Timestamp indicating when the task state was last updated
builtin_interfaces/Time stamp