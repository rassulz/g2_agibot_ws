std_msgs/Header         header

geometry_msgs/Vector3          gravity            # 重力向量
sensor_msgs/PointCloud2        ground_cloud       # 3d地面点云地图
sensor_msgs/PointCloud2        nonground_cloud    # 3d非地面点云地图
nav_msgs/OccupancyGrid         grid_map           # 2d栅格图
int32[]                        sc_descriptor      # lidar特征描述