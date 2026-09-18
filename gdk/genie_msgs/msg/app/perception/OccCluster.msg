int32 track_id            # Tracking ID of the clustered voxel object
int32 cluster_id          # Cluster ID of the voxel object
int32[] voxel_indices     # Indices of the occupied voxels belonging to this cluster
Point3D velocity          # Predicted velocity (vx, vy, vz) of the cluster; unit: m/s
int32 class_type          # Primary class label of the cluster
int32 sub_type            # Secondary class label of the cluster
int32 motion_status       # Motion status (static/dynamic) of the cluster