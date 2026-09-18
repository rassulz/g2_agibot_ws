Point3D pose                # Center position (x, y, z); unit: meters
Point3D size                # Size of the occupied voxel (l, w, h); unit: meters
Point3D velocity            # Velocity of the voxel (vx, vy, vz); currently unused; unit: m/s
int32 class_type            # Voxel class: 0=empty, 1=static, 2=dynamic, 3=ground
float32 class_type_score    # Voxel class type score [0, 1.0]
int32 sub_type              # Secondary voxel subtype; currently unused
int32 motion_status         # Motion status of the voxel; currently unused
int32 visible_status        # Visibility flag of the voxel; currently unused