uint64 request_id                       # reserved for serivce framework
TaskServiceResult  result               # Result of the navigation task
geometry_msgs/PoseStamped[] navi_poses  # navi poses
float32 cost                            # cost of the path, min cost is 0.0        