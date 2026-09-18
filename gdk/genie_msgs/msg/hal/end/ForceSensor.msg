# 详细说明见 - https://agirobot.feishu.cn/wiki/MPOLwmSm5iqF7Kk4sLacN3BtnNe
uint32    sensor_type  # 传感器类型 0 - Unknown, 1 - force, 2 - tactile, 3 - torque, 4 - fts             
string    sensor_name  # f"{frame}_{surface}_{sensor_type}", surface: "inner", "outer", "palmar", "dorsal"
string    frame        # 传感器安装所在的link名

uint32 rows         # 阵列行数 M
uint32 cols         # 阵列列数 N
 
float32 resolution_x    # 相邻两个cell在x方向的间距 [mm]（可选，没有就设0）
float32 resolution_y    # 相邻两个cell在y方向的间距 [mm]（可选，没有就设0）
 
 
# 下面是实际数值，按照 row-major 展开成一维数组，长度 = rows * cols
# index = row * cols + col
 
float32[] normal_force       # 法向力 [mN] 必选
float32[] shear_force_x      # 切向力x [mN]，如果没有就发空数组或同长度0， 按右手定则
float32[] shear_force_y      # 切向力y [mN]，如果没有就发空数组或同长度0， 按右手定则
bool[]    contact            # 是否接触
bool[]    valid              # 是否有效（若对应index处布局无传感器，则为false）

uint32    err_code