std_msgs/Header header

# 无效=0/休眠=1/全功率=2/低功率=3/换电=4/急停=5
uint8 power_state

# 无效=0，充电=1，放电=2
uint8 charge_state

# show detail msg
string power_status