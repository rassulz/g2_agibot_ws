int32 track_id              # Fused tracking ID
CameraObject[] cam_obj      # Camera object
BevObject bev_obj           # 3D object
GraspPoint[] grasp_point    # Grasp point positions
AssoMatrix[] asso_matrix    # Association matrices
int32 sensor_type           # Sensor type
int32 class_type            # Object class type
int32 sub_type              # Object subclass
int32 grasp_type            # Grasping type
int32 motion_status         # Object motion status
float32 tracking_time       # Object tracking duration
float32 tracking_score      # Object tracking confidence score
int32 coord_type            # 0: camera only, 1: lidar only, 2: both