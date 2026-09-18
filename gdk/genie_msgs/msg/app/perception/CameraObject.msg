int32 camera_id            # Camera ID
float32 cx                 # 2D bbox center x
float32 cy                 # 2D bbox center y
float32 width              # 2D bbox width
float32 height             # 2D bbox height
float32 depth              # Estimated depth of bbox
Point3D[] mask             # Segmentation mask points
Point3D[] keypoints        # Keypoints: pose_x, pose_y, confidence
Point3D ground_point       # 3D ground-contact point of bbox
int32 instance_id          # Object instance ID
float32 confidence         # Detection confidence
int32 class_type           # Object class
int32 sub_type             # Object subclass
int32 vip_flag             # VIP pedestrian flag
int32 motion_direction     # Pedestrian heading class
int32 occlusion_type       # Object occlusion type: 0 = no occlusion, 1 = ~30 % occluded, 2 = ~50 % occluded, 3 = ~70 % occluded
float32 occlusion_score    # Object occlusion score [0, 1]


Point3D pos                # Object center position (x, y, z) in camera coor.
Point3D size               # 3D box dimensions (length, width, height) in camera coor.
Point3D euler_angle        # Object orientation (Euler angles) in camera coor. # roll, pitch, yaw
float32[] rotation_matrix  # Object rotation matrix, 9 elements.
float32 pose_conf          # confidence of 6d pose.