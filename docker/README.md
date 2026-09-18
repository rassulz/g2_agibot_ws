# Docker development environment

Containers that reproduce the AgiBot G2's software stack on an x86_64
workstation, so the workspace builds against the same ROS 2 and Ubuntu
versions the robot runs.

See [`docs/g2_info.md`](../docs/g2_info.md) for the full survey these images
were derived from.

## Which image do I want?

Two targets are provided from one parameterized `Dockerfile`. They are not
interchangeable, and the right one depends on what you are building.

| | `kilted` (default) | `humble` |
|---|---|---|
| Ubuntu | **24.04 Noble** | 22.04 Jammy |
| ROS 2 | **Kilted** | Humble |
| Python | **3.12** | 3.10 |
| Matches the robot's runtime | **yes** | no |
| Matches GDK's x86_64 build target | no | **yes** |

**Use `kilted`** to build and test ROS 2 interfaces and nodes against the same
distro the robot runs. This is the default.

**Use `humble`** when linking the GDK's prebuilt x86_64 artifacts. Verified from
the contents of `server_installer.tar.gz`, the workstation-side binaries are:

```
app/gdk/build_dep/cpp/x86_64/lib/libgdk_adapter.so
app/gdk/build_dep/cpp/x86_64/lib/agibot_gdk.cpython-310-x86_64-linux-gnu.so
app/lib/python3.10/                       # the only bundled Python runtime
```

`cpython-310` is Ubuntu 22.04's system Python, and 22.04's ROS 2 is Humble —
which is why `gdk/scripts/ros_env.sh` offers only `humble` on `x86_64`.

**This is a hard constraint, not a preference:** the `kilted` image has Python
3.12, and a 3.12 interpreter cannot import a `cp310` extension module. If you
want `import agibot_gdk` to work, use the `humble` image.

The robot's own copy is `agibot_gdk.cpython-312-aarch64-linux-gnu.so` — Python
3.12 *and* aarch64 — so it will not load on either image. Take the x86_64 build
from the installer, never from `~/app` on the robot.

Both speak the same wire protocol. DDS interoperates across distros; matching
the distro matters for source and ABI compatibility, not for communication.

Note that the GDK core is not itself a ROS library — it speaks protobuf over
Fast DDS, and `examples/cpp` links `libgdk_adapter.so` with no `rclcpp` or ament
involved. The ROS distro matters for the interface packages and `examples/ros`,
and for the Python ABI the native module was built against.

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
