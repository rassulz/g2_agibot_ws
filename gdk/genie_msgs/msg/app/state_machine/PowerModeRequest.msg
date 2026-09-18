std_msgs/Header header

# 目标电源模式
# 无效 =0/ 休眠 = 1 /放电 = 2/充电 = 3 /低功率 = 4/换电 = 5
uint8 target_power_mode

# for battery swap give battery number
string target_info

# 无效=0/开关=1/HMI=2/远程=3/语音=4/
# 充电插入=5/外设插入=6/
# 急停=7/电池保护=8/
uint8 request_method
    
string uuid
string detail