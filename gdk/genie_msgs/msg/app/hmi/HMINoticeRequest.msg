std_msgs/Header header

# Feature notice request message, used to send various function-related notifications to HMI
# Message ID, used to identify a unique notification request
string id

# Name of the involved feature, e.g. "auto_docking" indicates automatic docking function
string feature

# Chinese notification text content
string text_chinese

# English notification text content
string text_english

# Text type, used to distinguish different types of notifications (such as prompt, warning, error, etc.)
string text_type

# Text priority, used by HMI to determine the display priority of notifications
string text_priority

float32 duration_time

string uuid
string detail