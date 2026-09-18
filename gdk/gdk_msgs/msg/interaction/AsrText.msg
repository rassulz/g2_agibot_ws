#触发唤醒后识别到的语音输入
#服务名:  /voice/asr/text
std_msgs/Header     header
string asr_text      # 文本内容
string requester     #请求方，触发源， "wakeup" - 语音唤醒 "vr" - vr按键唤醒

uint32 publish_ptp_ts
string publisher_id
uint32 counter
uint32 publish_ts