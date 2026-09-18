std_msgs/Header header
builtin_interfaces/Time publish_ts          # Timestamp when the perception result is published
builtin_interfaces/Time measuring_ts        # Trigger timestamp of the front LiDAR
FreeSpace[] freespace_list                  # Drivable areas represented by closed polygons (point chains)
Voxel[] voxel_list                          # Per-voxel occupancy status
OccCluster[] occcluster_list                # Clustered voxel results