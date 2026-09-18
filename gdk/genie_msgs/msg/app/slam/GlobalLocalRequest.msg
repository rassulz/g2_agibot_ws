std_msgs/Header         header

int32                   control            # 1：开始重定位， 0：结束重定位

int32                   relocalization_mode # 1: 给定初始位置的重定位   2: 其他（后续再定）
float32                 x                   # 初始x坐标
float32                 y                   # 初始y坐标
float32                 theta               # 初始朝向角度

# 作为唯一标识，匹配request和response
string uuid
string detail