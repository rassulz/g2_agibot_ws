
# 灯带区域名：head, waist_left, waist_right, back, chassis_front, chassis_left, chassis_right
string strip_name

# Individual RGB channel control (0-255)
uint8 red_light_intensity
uint8 green_light_intensity
uint8 blue_light_intensity

# Lighting control mode enumeration
uint8 LIGHTING_MODE_SYNC = 0
uint8 LIGHTING_MODE_SEQUENCE = 1
uint8 LIGHTING_MODE_REVERSE_SEQUENCE = 2

# Selected lighting control mode
uint8 lighting_mode
