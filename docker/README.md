# Docker development environment

Containers that reproduce the AgiBot G2's software stack on an x86_64
workstation, so the workspace builds against the same ROS 2 and Ubuntu
versions the robot runs.

See [`docs/g2_info.md`](../docs/g2_info.md) for the full survey these images
were derived from.

## Which image do I want?

Two targets are provided from one parameterized `Dockerfile`. They serve
different purposes -- pick by what you are doing, not by preference.

### `kilted` -- writing code that will run on the robot (default)

This is the primary development environment. Code is written and built here,
pushed to git, then pulled and rebuilt on the robot. The container matches the
robot's runtime exactly:

| | Container | Robot |
|---|---|---|
| Ubuntu | 24.04 | 24.04 |
| ROS 2 | Kilted | Kilted |
| Python | 3.12 | 3.12 |

Matching matters because ROS 2 distros are not source-compatible: Kilted's
`rosidl`, QoS defaults and `rclpy`/`rclcpp` APIs differ from Humble's. Building
against Kilted here means what compiles on your workstation compiles on the
robot.

**Architecture is the one thing that does not match.** The container is x86_64;
the robot is aarch64. Source is portable, compiled objects are not -- so ship
source through git and run `colcon build` on the robot. Never copy `build/` or
`install/` across.

### `humble` -- connecting to the robot over DDS from the workstation

Only needed when the workstation itself talks to the robot: inspecting live
topics, teleoperation, or using the GDK Python API.

| | Container | Reason |
|---|---|---|
| Ubuntu | 22.04 | GDK's x86_64 payload is built for it |
| ROS 2 | Humble | AgiBot's DDS profile uses the Fast DDS **2.x** XML schema |
| Python | 3.10 | the shipped binding is `cpython-310` |

Two hard constraints, both verified:

1. `conf/dds/gdk_ros_domain.xml` uses `<discoveryServersList>`/`<RemoteServer>`,
   which Fast DDS 3.x (Kilted) refuses to parse:
   `XMLPARSER Error: Node 'discoveryServersList' without content`.
   The same file loads fine under Humble and discovers the robot's topics.
2. `import agibot_gdk` needs Python 3.10 -- a 3.12 interpreter cannot load a
   `cp310` extension module.

### Summary

| Task | Container |
|---|---|
| Write nodes and interfaces to deploy on the robot | **`kilted`** |
| `ros2 topic list` / `echo` against the live robot | **`humble`** |
| `import agibot_gdk` | **`humble`** |
| Build message packages | either -- both verified |

## Quick start

```bash
# Build (from the repository root)
docker compose -f docker/docker-compose.yml build kilted

# Interactive shell
docker compose -f docker/docker-compose.yml run --rm kilted

# One-off command
docker compose -f docker/docker-compose.yml run --rm kilted ros2 interface list
```

Inside the container:

```bash
cb                              # colcon build into the per-distro base
cb --packages-select genie_msgs # build one package
ros2 interface show genie_msgs/msg/JointState
```

## Build artifacts are kept per distro

The repository root already carries `build/`, `install/` and `log/` from a
host-side Humble build. Writing a second distro's artifacts into those same
directories corrupts both, so the container builds into a subdirectory instead:

```
build/kilted/      install/kilted/      log/kilted/
build/humble/      install/humble/      log/humble/
```

The `cb` helper and the entrypoint's overlay sourcing both use these paths. If
you call `colcon` directly, pass them yourself:

```bash
colcon build --build-base build/$ROS_DISTRO --install-base install/$ROS_DISTRO
```

Your existing host-level `build/` and `install/` are left untouched.

## Talking to the robot

The container runs with `network_mode: host` and `ipc: host`. DDS discovery is
multicast and peer-to-peer, and Fast DDS uses POSIX shared memory for same-host
transport; bridged networking breaks both. Because of this the container shares
the host's interfaces directly — no port mapping is needed or possible.

Defaults match `gdk/scripts/ros_env.sh` on the robot:

| Variable | Value |
|---|---|
| `ROS_DOMAIN_ID` | `4` |
| `RMW_IMPLEMENTATION` | `rmw_fastrtps_cpp` |

To load the robot's Fast DDS profile, fetch it and point `DDS_PROFILE_FILE` at
your copy:

```bash
# The robot serves it over HTTP on port 8849
curl -o dds/gdk_ros_domain.xml http://192.168.1.224:8849/gdk_ros_domain.xml

DDS_PROFILE_FILE=/ws/dds/gdk_ros_domain.xml \
  docker compose -f docker/docker-compose.yml run --rm kilted
```

The entrypoint exports both `FASTRTPS_DEFAULT_PROFILES_FILE` and
`FASTDDS_DEFAULT_PROFILES_FILE` — the variable was renamed in Fast DDS 3.x, so
Humble reads the first and Kilted the second.

### The profile needs editing first

`gdk_ros_domain.xml` contains `${DEV_IP}` placeholders in its
`interfaceWhiteList` entries. On the robot, `ros_env.sh` rewrites them in place
with an address derived from `ip route get 10.42.1.101`. That route only exists
on the robot's internal 10 GbE network, so on a WiFi-only workstation the
detection fails and you must substitute your own address by hand:

```bash
sed -i "s|\${DEV_IP}|192.168.1.x|g" dds/gdk_ros_domain.xml
```

Note that the documented GDK path assumes the workstation is wired into
`10.42.1.0/24` rather than reaching the robot over WiFi.

## Using the GDK inside the container

`$HOME/.cache/agibot` on the host is mounted at `/home/dev/.cache/agibot` —
this is the `GDK_HOME` location that `gdk/scripts/install.sh` and the examples'
`CMakeLists.txt` expect. When that directory contains an install, the entrypoint
adds it to `PYTHONPATH` and `LD_LIBRARY_PATH` and sets `APP_CONF_PATH`.

To populate it, fetch the workstation installer from the robot:

```bash
mkdir -p ~/.cache/agibot
curl -o ~/.cache/agibot/server_installer.tar.gz \
     http://192.168.1.224:8849/server_installer.tar.gz
tar -zxf ~/.cache/agibot/server_installer.tar.gz -C ~/.cache/agibot
```

`install.sh` hardcodes `http://10.42.1.101:8849`, which is only reachable from
the robot's internal network — hence fetching directly from the WiFi address
above rather than running that script unmodified.

## Options

| Variable | Default | Effect |
|---|---|---|
| `USER_UID` / `USER_GID` | `1000` | Container user ids. Must match your host ids so files written into the mounted workspace stay yours. |
| `INSTALL_VIZ` | `0` | Set to `1` at build time to add `rviz2`, `rqt` and common plugins. |
| `ROS_DOMAIN_ID` | `4` | DDS domain. Must match the robot. |
| `DDS_PROFILE_FILE` | unset | Path *inside the container* to a Fast DDS profile XML. |
| `DISPLAY` | inherited | X11 passthrough for GUI tools. |

```bash
# Image including the visualization stack
docker compose -f docker/docker-compose.yml build \
  --build-arg INSTALL_VIZ=1 kilted

# Allow GUI applications through X11 (host side, once per session)
xhost +local:docker
```

## Files

| File | Purpose |
|---|---|
| `Dockerfile` | Parameterized image, `ROS_DISTRO` selects the base. |
| `docker-compose.yml` | The `kilted` and `humble` services and their shared runtime config. |
| `entrypoint.sh` | Sources the underlay and overlay, sets DDS and GDK environment, provides `cb`. |
| `../.dockerignore` | Keeps host build artifacts out of the build context. |
