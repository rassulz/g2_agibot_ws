string name # 物体名称, 空为不指定
string parent_frame # e.g. base_link
geometry_msgs/Pose parent_tf_obj # 物体相对于parent_frame的位姿

uint8 COLLISION_ENV = 0
uint8 COLLISION_OTHER_OBJ = 1
uint8 COLLISION_TARGET_OBJ = 2

uint8 COLLISION_ROBOT_BASE = 11
uint8 COLLISION_ROBOT_BODY = 12
uint8 COLLISION_ROBOT_HEAD = 13
uint8 COLLISION_ROBOT_LEFT_ARM = 14
uint8 COLLISION_ROBOT_RIGHT_ARM = 15
uint8 COLLISION_ROBOT_TOOL = 16

uint8 COLLISION_ATTACHED_OBJ = 21
uint8 COLLISION_ATTACHED_CAMERA = 22
uint8 collision_type

GeometryInfo geometries
bool collidable
bool is_static

string task_tags # 给task planner储存额外信息，本身不参与运控计算

# deprecated DO NOT USE!
uint8 ADD_OBJ = 0
uint8 UPDATE_OBJ = 1
uint8 REMOVE_OBJ = 2
uint8 operation # 对物体的操作 0: 添加 1: 更新 2: 删除
