# g2_agibot_ws

ROS 2 workspace for the **AgiBot G2** humanoid, with a reproducible Docker
development environment matching the robot's onboard software stack.

## Contents

| Path | Description |
|---|---|
| [`gdk/genie_msgs/`](gdk/genie_msgs) | Robot-internal ROS 2 interfaces (136 messages, 7 service groups) |
| [`gdk/gdk_msgs/`](gdk/gdk_msgs) | The GDK-facing API — the `/gdk/*` namespace you program against (29 messages) |
| [`docker/`](docker) | Containers reproducing the robot's Ubuntu + ROS 2 versions — see [docker/README.md](docker/README.md) |
| [`docs/g2_info.md`](docs/g2_info.md) | Full read-only survey of the robot: hardware, OS, networking, directory layout, GDK internals |

Message definitions are vendored from the robot's `~/app/ros_msg/` at
**GDK 3.2.3** and are MIT licensed by AgiBot.

## Target system

The robot this workspace targets:

| | Robot | Supported workstation |
|---|---|---|
| Board | NVIDIA Jetson AGX Thor (`aarch64`) | `x86_64` |
| OS | Ubuntu 24.04 | Ubuntu 22.04 |
| ROS 2 | Kilted | Humble |
| Python | 3.12 | 3.10 |
| GDK | 3.2.3 | 3.2.3 |

Both are provided as container images, because the split is not cosmetic:
the GDK's x86_64 Python binding is built `cpython-310`, so `import agibot_gdk`
requires the Humble image, while ROS interface work should match the robot's
Kilted. Details in [docker/README.md](docker/README.md).

## Quick start

```bash
docker compose -f docker/docker-compose.yml build kilted
docker compose -f docker/docker-compose.yml run --rm kilted

# inside the container
cb                    # colcon build into build/kilted + install/kilted
source install/kilted/setup.bash
ros2 interface list | grep gdk_msgs
```

## Communication model

The robot's native transport is **protobuf over Fast DDS** (`aorta` /
`cosine_bus`). ROS 2 is a bridge layer configured by the GDK's
`ros_bridge_config.json`, which maps internal topics into the `/gdk/*`
namespace:

| Internal | | GDK |
|---|---|---|
| `/hal/joint_state` | → | `/gdk/joint_state` |
| `/wbc/motion_control_status` | → | `/gdk/motion_control_status` |
| `/gdk/joint_pos_request` | → | `/MotionControlService/JointPosition/request` |

Connecting to the robot requires `ROS_DOMAIN_ID=4`,
`RMW_IMPLEMENTATION=rmw_fastrtps_cpp` and the robot's Fast DDS profile.
See [docker/README.md](docker/README.md#talking-to-the-robot).

## Documentation

The authoritative GDK 3.2.3 documentation is served by the robot itself on
port 8849 (`app/gdk/site/`, a searchable MkDocs site). Prefer it over the
public `support.agibot.com` pages, which document GDK 2.4.2.

## License

Apache 2.0 — see [LICENSE](LICENSE). Vendored `genie_msgs` and `gdk_msgs`
message definitions are MIT, © AgiBot.
