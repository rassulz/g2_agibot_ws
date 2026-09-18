# topic名： /hal/agv_fallback 在fallback模型下，控制底盘回退，发送频率10Hz, 500ms未收到数据则自动停止
std_msgs/Header     header
uint32               type   # 0 停止 1：继续