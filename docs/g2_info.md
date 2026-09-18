# AgiBot G2 — Machine Reference

Read-only survey of the robot's onboard computer, collected over SSH.
Nothing on the robot was modified.

| | |
|---|---|
| **Surveyed** | 2026-09-18 |
| **Host** | `<user>@<robot-ip>` over WiFi (this survey: `192.168.1.224`) |
| **Hostname** | `localhost.localdomain` |
| **Robot AID** | `G2A0005C502657` (type `G2A`, customer `genie`) |
| **App release** | `genie_g02_rb_2.3.1_ac56d942_2026-06-03-17-49-44_thor.tar.gz` |
| **GDK version** | **3.2.3** (commit `1802ca1`, built 2026-05-19) |

> The `support.agibot.com` link in the repo README points at **GDK 2.4.2**.
> This robot runs **3.2.3** — use `?gdk_version=3.2.3` or the onboard docs instead.

---

## 1. Hardware

| Item | Value |
|---|---|
| Board | **NVIDIA Jetson AGX Thor Developer Kit** |
| Architecture | `aarch64` (ARMv9, SVE2, bf16/i8mm) |
| CPU | 14 cores, single cluster, 54 MHz – 2601 MHz |
| RAM | **120 GiB**, no swap |
| L1 cache | 896 KiB data + 896 KiB instruction (14 instances) |

### Storage

| Mount | Device | Size | Used |
|---|---|---|---|
| `/` | overlay | 26 G | 20% |
| `/data` | `nvme0n1p4` | **1.5 T** | 3% |
| `/shared/head` | `nvme0n1p2` | 98 G | 1% |
| `/shared/pad` | `nvme0n1p1` | 98 G | 1% |
| `/shared/tmp` | `nvme0n1p3` | 196 G | 1% |
| `/boot/efi` | `nvme1n1p5` | 505 M | 1% |

Root is an **overlay** filesystem — treat `/` as disposable and keep
persistent work under `/data`.

---

## 2. Operating system

| Item | Value |
|---|---|
| Distro | **Ubuntu 24.04.3 LTS (Noble Numbat)** |
| Kernel | `6.8.12-rt-tegra` — **PREEMPT_RT** (`/sys/kernel/realtime` = 1) |
| L4T / JetPack | R38.4.0 (`nvidia-l4t-core 38.4.0-20251230160601`), GCID 43443517 |
| Python | **3.12.3** (`/usr/bin/python3`), pip 26.1.2 |
| Timezone | **Asia/Shanghai (CST, +0800)** |
| Clock | NTP active via `chrony`, synchronized |
| Container | No — bare metal (`/proc/1/cgroup` = `0::/init.scope`) |

The kernel is a **real-time** build. That is why motion control, HAL and
EtherCAT run with usable latency, and why CPU affinity / cgroup configs
exist under `conf/resource_quotas/`.

> Some log files carry **1970** timestamps (`scene_control.log.INFO.19700101-*`),
> meaning the clock was unset on those boots before NTP acquired. Relevant when
> correlating logs across machines.

---

## 3. ROS 2

| Item | Value |
|---|---|
| Distro installed | **`kilted`** — `/opt/ros/kilted` (203 packages) |
| Sourced by default? | **No** — `$ROS_DISTRO` is empty on plain login |
| `ROS_DOMAIN_ID` | **4** (set by `gdk/scripts/ros_env.sh`) |
| RMW | **`rmw_fastrtps_cpp`** |
| Fast DDS | 3.2.2 (Fast CDR 2.3.0) |

### Dev-host distro matrix

From `gdk/scripts/ros_env.sh`, the GDK itself selects the distro by architecture:

| Arch | ROS distro |
|---|---|
| `x86_64` | **`humble`** only |
| `aarch64` | `kilted` preferred, falls back to `humble` |

**An x86_64 / Ubuntu 22.04 / Humble workstation is the supported dev host.**
The robot running Noble + Kilted is expected and not a conflict — the two sides
interoperate over Fast DDS on domain 4, not by sharing a distro.

---

## 4. Networking

Extensive multi-homed setup. WiFi is the general-access path; the `10.42.x.x`
VLANs are the robot's internal fabric.

| Interface | Address | Role |
|---|---|---|
| `wlan0` | **192.168.1.224/24** | WiFi, default route via `192.168.1.1` |
| `xfi2.10g@mgbe2_0` | **10.42.1.101/24** | 10 GbE — **primary internal bus** |
| `xfi0.20@mgbe0_0` | 10.42.0.101/24 | internal VLAN 20 |
| `xfi0.60@mgbe0_0` | 10.42.0.60/24 | internal VLAN 60 |
| `xfi0.80@mgbe0_0` | 10.42.80.101/24 | internal VLAN 80 |
| `xfi3.90@mgbe3_0` | 10.42.2.101/24 | internal VLAN 90 |
| `pad` | 10.42.6.101/24 | tablet / pad link |
| `ecat0/1/2@mgbe1_0` | — | **EtherCAT** (motor buses) |
| `can0`–`can5` | — | CAN buses |
| `wwan0`, `p2p0`, `wifi-aware0`, `wlanap0` | down | cellular / P2P / AP mode |

**`10.42.1.101` is the robot's own service address** — `AORTA_URI`,
`LOCATOR_IP` and `AORTA_DISCOVERY_URI` (`:2379`) all point there.

### Open ports of interest

| Port | Service |
|---|---|
| **8849** | GDK HTTP distribution server (installers, docs, DDS profile) |
| **8850** | same over HTTPS (self-signed cert in `/data/logs/`) |
| 2379 | aorta discovery (etcd-style) |
| 53 / 67 / 68 | dnsmasq (DHCP+DNS for internal nets) |
| 5353 | avahi / mDNS |

Both 8849 and 8850 are **currently listening**, and 8849 answered `HTTP 200`
from the workstation over WiFi.

---

## 5. Directory layout

### `/home/agi` (user `agi`)

```
app/                          main application install (see below)
base-remote.sh                remote-mode launcher
toolkit.tgz            (25 M) dev toolkit archive
serialDeserialSample_1119.tgz (28 M) serialization sample
narwhal_a2d.tar.gz     (51 M) narwhal A2D package
test_video.mp4
Desktop/                      stock Jetson desktop shortcuts
```

### `/home/agi/app` — the application root

| Path | Contents |
|---|---|
| `bin/` | **307 executables** — `hal`, `dds_*`, `camera_*`, `cosine_*`, `aorta`, `dlb`, `doctor` … |
| `lib/` | shared libraries (abseil, Fast DDS, OpenCV, PCL, gRPC, `hal`, `agora`, `agibot_voice`, `engines-3`) |
| `conf/` | runtime configuration — **see §7** |
| `config/` | additional config tree |
| `gdk/` | **the SDK** — see §6 |
| `head/` | head-unit payload: own `bin/` incl. `protoc`, `fast-discovery-server`, gRPC plugins, `agibot_voice_test` |
| `ros_msg/` | **13 ROS 2 interface packages** — see §8 |
| `python/` | `perfmonkit` (Jetson telemetry, `.pyc` only) |
| `share/` | ament index, URDF descriptions, `gdk_msgs`, `genie_msgs`, licenses, OpenCV, pinocchio, `teleop_it` |
| `tools/` | `fastdds` CLI helpers (`discovery`, `shm`, `xml_ci`) |
| `apk/` | Android packages (tablet / pad UI) |
| `narwhal/` | narwhal component |
| `logs` | symlink → `/data/logs/latest` |
| `env.sh` | environment setup — extends `LD_LIBRARY_PATH`, `PATH`, `PYTHONPATH` |
| `dds_view_env.sh` | same plus `FASTDDS_DEFAULT_PROFILES_FILE=conf/dds/dds_view.xml` |
| `.version` / `.pkg_version` | release tag / full dependency manifest |

### `/data`

```
logs/           runtime logs (app/logs points here)
record/         DDS recordings
camera_record/  camera captures
parameters/     sensor calibration  (/data/parameters/sensor/)
version/        aid_info.yaml — robot identity
ota/, ota_payload_package/, ota_work/   OTA update staging
dlb/, hmi_proxy/, launcher/, backup/
```

---

## 6. The GDK — `/home/agi/app/gdk`

**Version 3.2.3**, commit `1802ca1`, built 2026-05-19. This is a genuine SDK:
headers, libraries, examples and installers, not just a runtime.

| Path | Contents |
|---|---|
| `examples/cpp/` | 8 C++ samples: `mc`, `pnc`, `camera`, `imu`, `lidar`, `robot_body`, `slam`, `control_mode` |
| `examples/python/` | 14 demos: `robot_demo`, `mc_example`, `pnc_example`, `servo_control`, `move_chassis`, `camera_demo`, `camera_web_viewer`, `lidar_demo`, `imu_demo`, `uss_demo`, `slam_demo`, `interaction_demo`, `hd_bt_navigation_example`, `pb_to_mcap` |
| `examples/ros/` | 2 ament packages: `camera_example`, `control_example` |
| `build_dep/cpp/aarch64/` | `include/` + `lib/libgdk_adapter.so` (**aarch64 only on the robot**) |
| `build_dep/python/python_wheels/` | `genie_msgs_pb-1.5.1-py3-none-any.whl` — **`py3-none-any`, architecture-independent** |
| `build_dep/python/pybind/` | pybind11 source package (`setup.py`, needs pybind11 ≥ 2.6, numpy ≥ 1.19, Python 3.8+) |
| `build_dep/ros/genie_msgs/` | ROS interface sources |
| `lib/` | **`agibot_gdk`** Python module + 23 protobuf message packages |
| `site/` | **full MkDocs documentation site**, searchable (`search/search_index.json`) |
| `web/` | browser UI (`index.html`, css, js) |
| `config/` | `app_conf.json`, `ros_bridge_config.json`, `mc_impl_config.json`, camera confs, `diagnostics.yaml`, `robot_resources.json` |
| `scripts/` | install / env / deploy helpers — see below |
| `installer/` | `server_installer.tar.gz` (**212 M**), `examples.tar.gz` (53 K) |
| `aim_master/`, `corobot/` | AIM master resources; corobot client |

### `gdk/lib` Python packages

`agibot_gdk` (native module — `agibot_gdk.cpython-312-aarch64-linux-gnu.so`, so
**Python 3.12 / aarch64 on the robot**) plus generated protobuf bindings:

```
builtin_interfaces_pb  conv_pb          dlb_msgs_pb       fsm_msgs_pb
genie_msgs_pb          geometry_msgs_pb gma_msgs_pb       hmi_msgs_pb
mc_msgs_pb             monitor_msgs_pb  nav_msgs_pb       pnc_msgs_pb
rh_msgs_pb             rh_msgs_grpc_pb  rh_msgs_v4_pb     rh_msgs_v4_grpc_pb
sensor_msgs_pb         shape_msgs_pb    std_msgs_pb       std_srvs_pb
tf2_msgs_pb            visualization_msgs_pb
```

### Key scripts

| Script | Purpose |
|---|---|
| `install.sh` | Installs GDK to `~/.cache/agibot/`. Fetches `server_installer.tar.gz` **and** `gdk_ros_domain.xml` from `http://10.42.1.101:8849/`. |
| `install_example.sh` | Fetches `examples.tar.gz` from the same server. |
| `ros_env.sh` | **The main dev-side env script.** Picks distro by arch, sets `ROS_DOMAIN_ID=4`, `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`, auto-detects `DEV_IP` via `ip route get 10.42.1.101`, rewrites the DDS profile's `interfaceWhiteList` with that IP, restarts the ROS 2 daemon. |
| `install_ros_env.sh` | Installs the ROS environment. |
| `deploy_gdk_msgs.sh` | Flattens `share/gdk_msgs/share/gdk_msgs/**/*.msg` into a **generated ament package** (`msg/` + `CMakeLists.txt` + `package.xml`). Errors out on duplicate basenames. Default target: `gdk/examples/ros/gdk_msgs`. |
| `prepare_server.sh` | Symlinks installers, scripts, docs and `gdk_ros_domain.xml` into `/data/logs/`, creates self-signed cert. |
| `start_http_server.sh` | Serves that directory on **8849 (HTTP)** and **8850 (HTTPS)**; adds a `/gdk_version` JSON endpoint. |
| `ptp_client.sh` / `ptp_server.sh` / `ptp_hard.sh` | PTP clock synchronization. |
| `install_a2d.sh` | A2D component install. |

### `GDK_HOME` convention

`~/.cache/agibot` — the C++ `CMakeLists.txt` resolves headers and
`libgdk_adapter.so` from `$GDK_HOME/app/gdk/build_dep/cpp/<arch>/`, selecting
`x86_64` or `aarch64` from `CMAKE_SYSTEM_PROCESSOR`.

---

## 7. Configuration — `app/conf`

### `conf/sys/run.conf` — master runtime switches

```
PRODUCT_GENERATION=2
ENABLE_GDK=0
ENABLE_G02_GDK=1            # G2 GDK active
ENABLE_PERFGUARD=1
APP_DIR=/home/agi/app
LOG_PATH=/data/logs/
AORTA_URI=http://10.42.1.101
LOCATOR_IP=10.42.1.101
AORTA_DISCOVERY_URI=http://10.42.1.101:2379
DEFAULT_LAUNCH_SCENE=base
COSINE_BUS_DEFAULT_MIDDLEWARE=aorta
FASTDDS_PARTICIPANT_PROFILE=FastDDSProfile
FASTDDS_DEFAULT_PROFILES_FILE=$APP_DIR/conf/dds/fastdds_profile.xml
COSINE_ENABLE_ROS_TOPIC_PREFIX=1
```

With `ENABLE_G02_GDK=1`, `env.sh` exports
`PYTHONPATH=$APP_DIR/gdk/lib` and `APP_CONF_PATH=$APP_DIR/gdk/config/app_conf.json`.

### `conf/dds/` — DDS profiles

| File | Use |
|---|---|
| `gdk_ros_domain.xml` | **cross-machine** (x86_64 dev host). Domain **4**; SHM + UDP + client TCP transports; `<address>${DEV_IP}</address>` placeholders rewritten by `ros_env.sh`; server at `10.42.1.101`. |
| `gdk_ros_local.xml` | on-robot (aarch64) profile |
| `fastdds_profile.xml` | default participant profile |
| `dds_view.xml` | for the `dds_view` tool |
| `base_fastdds.prototxt`, `camera_fastdds.prototxt`, `gdk_fastdds.prototxt`, `cosine_ipc.prototxt` | cosine bus / IPC topic configs |

### `conf/manifest.d/` — launch scenes

`base.json` (default), `base-fastdds.json`, `base-o10.json`, `base-remote.json`,
`base-rl.json`, `develop.json`, `idle.json`.

Each lists apps with `path`, `arguments`, `env` and `delay`. `base.json` starts
`hal`, `hal_lowerlimb`, `camera_service`, `cosine_runner`, `camera_dlb`,
`teleop_it`, …

### Other config subtrees

`aorta/` (diagnosis, PCIe, co_pilot) · `dlb/` (data logging, certs, `A2D_viz.urdf`,
rule/data configs) · `imu/` · `edge-link/` · `media_manager/` · `record/` ·
`resource_quotas/` (cgroups, `rt_config.json`) · `agibot_voice/` · `cosine_system/`

---

## 8. Message interfaces

### `app/ros_msg` — 13 ROS 2 packages

| Package | msg | srv | Domain |
|---|---:|---:|---|
| `hmi_msgs` | **151** | 0 | Human-Machine Interface — face/screen, bluetooth, disk, AID info |
| `rh_msgs_v4` | **129** | 0 | robot hardware v4 |
| `pnc_msgs` | 44 | 0 | planning & control |
| `rh_msgs` | 43 | 0 | robot hardware |
| `dlb_msgs` | 13 | 0 | data logging bus |
| `mc_msgs` | 13 | 0 | motion control |
| `monitor_msgs` | 11 | 0 | **system health telemetry — not the face screen** |
| `aimdk_msgs` | 10 | 4 | AIM development kit |
| `gma_msgs` | 10 | 0 | — |
| `proto2ros` | 7 | 0 | protobuf↔ROS conversion |
| `fsm_msgs` | 6 | 0 | finite state machine |
| `gdk_msgs` | 6 dirs | 1 | **the GDK-facing API** |
| `genie_msgs` | 5 dirs | 7 dirs | internal robot API |

`genie_msgs` subdirectories — msg: `app`, `common`, `hal`, `remote`, `voice`;
srv: `app`, `body`, `hal`, `hmi`, `remote`, `voice`, `wbc`.

### `gdk_msgs` — the 29 messages you actually program against

```
common/          CommonRequest, CommonResponse
hal/             JointState, WholeBodyStatus
interaction/     AsrText, VideoDisplay
motion_control/  EndEffectorPoseControl, JointPositionRequst,
                 JointPositionServo, MotionControlStatus
pnc/             NormalNavigationRequest/Response, NormalNaviPathCostRequest/Response,
                 TaskCancelRequest/Response, TaskPauseRequest/Response,
                 TaskResumeRequest/Response, TaskHeader, TaskServiceResult, TaskState
slam/            GuidePtInfo, HmiMap, HmiMapInfo, MapInfo, OdomInfo, PolygonInfo
```

Generate the buildable ament package with `deploy_gdk_msgs.sh`; do not
hand-copy.

### Architecture — protobuf over DDS, bridged to ROS

The native transport is **protobuf over Fast DDS** (via the `aorta` / `cosine_bus`
middleware). **The GDK core is not a ROS library** — `server_installer.tar.gz`
contains no `/opt/ros` payload and no ROS references, and `examples/cpp/CMakeLists.txt`
links `libgdk_adapter.so` alone, with no `rclcpp` and no ament. ROS 2 enters only
through `examples/ros/` and the interface packages.

ROS 2 messages are a **bridge layer**, mapped by
`gdk/config/ros_bridge_config.json`:

| Internal topic | ⇄ | GDK topic |
|---|---|---|
| `/hal/joint_state` | → | `/gdk/joint_state` |
| `/MotionControlService/JointPosition/request` | ← | `/gdk/joint_pos_request` |
| `/MotionControlService/JointPosition/response` | → | `/gdk/joint_pos_response` |
| `/wbc/motion_control_status` | → | `/gdk/motion_control_status` |
| `/wbc/joint_control` | ← | `/gdk/joint_control` |

**`/gdk/*` is your namespace.** Internal `/hal/*`, `/wbc/*` and
`/MotionControlService/*` topics are behind the bridge.

---

## 9. Running system

### Active processes (top CPU)

`hal` 30% · `camera_service` 23% · `cosine_runner` 21% · `genie_motion_co` 20% ·
`camera_dlb` 16% · `quark_navigatio` 16% · `lidar` 11% · `run_corobot_app` 9% ·
`hal_lowerlimb` 8% · `dds_record` 7% · `camera_rtc` 6% · `fault_manager` 6% ·
`dr_state_machin` · `slam_state_mach` · `pico_adapter` · `monitor_app` ·
`media_manager` · `tagloc_state_ma` · `power_manager` · `arbitrator_runn` ·
`teleop_main_nod` · `dlb`

Plus RT IRQ threads for CAN (`irq/293-can1`, `irq/311-can0`) and EtherCAT
(`irq/315-mgbe1_0`).

> Load average was **~20 on 14 cores** during the survey — the robot is busy
> even at idle. Budget headroom for your own nodes.

### Notable systemd services

`genie_app.service` (main application) · `aorta.service` · `bsp_manager.service`
(G2 board support) · `agibot_perfguard.service` · `jtop.service` ·
`nvargus-daemon.service` (camera) · `chrony.service` (NTP) ·
`collectd.service` · `nvfancontrol.service` · `gdm.service` ·
`gnome-remote-desktop.service` · `lttng-sessiond.service`

---

## 10. Software stack (from `.pkg_version`)

### AgiBot / Genie components

`agibot_gdk 3.2.3` · `aorta 2.2.0` · `cosine_bus 3.7.0` · `cosine_runner 2.0.23` ·
`cosine_lord 2.1.0` · `cosine_inf 2.1.0` · `cosine_dal 2.0.0` ·
`cosine_scheduler 2.0.1` · `cosine_plugin 2.0.1` · `hal rc-2.2.13-3` ·
`motion-control 0.5.34-rb230` · `navigation 1.2.7` · `slam 1.1.18` ·
`lidar 2.3.0` · `camera 3.4.5` · `imu 1.1.1` · `teleop_it 4.0.24` ·
`corobot 2.0.0` · `dlb 0.25.0` · `dds_view 2.4.0` · `dds_record 2.2.0` ·
`fault_manager rc-1.1.2` · `monitor_app 1.1.1` · `hmi_proxy 1.1.1` ·
`agibot_voice 1.0.9` · `genievisionpro 2.4.32` · `genie_robot_description 1.2.10` ·
`genie_pb_messages 1.5.1` · `gdk_messages 0.0.1` · `tagloc 2.2.27` ·
`perf_guard 1.2.6` · `remote_hal 0.1.2` · `edge-link 1.1.2` · `freespace 1.1.16` ·
`launcher 2.21.2` · `media_manager 0.0.11` · `gx_rtc_engine 2.0.4`

### Third-party highlights

Fast DDS 3.2.2 · protobuf 28.3 · gRPC 1.70.0 · OpenCV 4.13.0 · PCL 1.13.1 ·
Eigen 3.4.0 · **Pinocchio 3.3.0** · GTSAM 4.2 · Ceres 2.2.0 · FCL 0.7.0 ·
octomap 1.9.7 · nlopt 2.7.1 · qpOASES 3.2.1 · BehaviorTree.CPP 4.6.2 ·
Boost 1.83.0 · CPython 3.12.7 · FFmpeg 4.4.4 · VTK 9.1.0 · abseil 20250127.0 ·
urdfdom 4.0.0 · paho-mqtt · uWebSockets 20.70.0

The presence of Pinocchio, GTSAM, FCL, nlopt and qpOASES indicates whole-body
dynamics, factor-graph SLAM, collision checking and QP-based control onboard.

---

## 11. Robot models

`app/share/genie_robot_description/urdf/` ships 8 variants:

```
G1   G2H_t0_acs   G2L_lg_crs   G2S_t0_crsP
G2_t2_crs   G2_t2_crsB   G2_t2v2_crs   G2_t2v2_crsB
```

URDF root is configured in `gdk/config/app_conf.json`:

```json
{
  "cam_dev_conf_path": "/home/agi/app/conf/deploy/develop/",
  "camera_config_path": "/data/parameters/sensor/",
  "app_version_path": "/home/agi/app/.version",
  "robot_aid_path": "/data/version/aid_info.yaml",
  "urdf_path": "/home/agi/app/share/genie_robot_description/urdf/"
}
```

---

## 12. Documentation

A complete **MkDocs site for GDK 3.2.3** is on the robot at `app/gdk/site/`,
symlinked into `/data/logs/site` and served on port 8849. It includes a
searchable index (`search/search_index.json`) and a Dockerfile for standalone
hosting (`site/docker/`).

This is the authoritative documentation for this robot — more accurate than the
public 2.4.2 pages the repo README links to.

---

## 13. Notes for workstation setup

**Workstation surveyed:** x86_64, Ubuntu 22.04.5, ROS 2 Humble, Python 3.10.12,
colcon present — this matches the `x86_64 → humble` branch of `ros_env.sh` and is
the supported configuration.

1. **Never copy `~/app` wholesale.** The robot is aarch64; compiled objects there
   (`libgdk_adapter.so`, `agibot_gdk.cpython-312-aarch64-linux-gnu.so`, everything
   in `app/lib`) will not load on x86_64. Use `server_installer.tar.gz`, which
   carries the workstation build.

2. **Python version gap — verified from the installer's contents.**
   `server_installer.tar.gz` carries prebuilt binaries for *both* architectures,
   each compiled against that side's system Python:

   | Path in the installer | ABI tag |
   |---|---|
   | `app/gdk/build_dep/cpp/x86_64/lib/agibot_gdk...so` | **`cpython-310-x86_64-linux-gnu`** |
   | `app/gdk/build_dep/cpp/aarch64/lib/agibot_gdk...so` | `cpython-312-aarch64-linux-gnu` |
   | `app/gdk/lib/agibot_gdk/agibot_gdk...so` | **`cpython-310-x86_64-linux-gnu`** |

   The only Python runtime bundled is `app/lib/python3.10/`. **CPython 3.10 is
   Ubuntu 22.04's system Python, and 22.04's ROS 2 is Humble** — that is the
   whole reason `ros_env.sh` offers only `humble` on `x86_64`.

   The pure-protobuf wheel (`genie_msgs_pb-1.5.1-py3-none-any.whl`) is
   `py3-none-any` and portable anywhere. The native `agibot_gdk` module is not:
   a Python 3.12 interpreter will refuse to import the `cp310` build.

3. **`install.sh` hardcodes `http://10.42.1.101:8849`**, which is only reachable
   from the robot's internal 10 GbE network. Over WiFi the same server answers on
   `http://192.168.1.224:8849` (verified, HTTP 200), so either edit a local copy
   of the script or fetch the artifacts directly.

4. **`ros_env.sh` derives `DEV_IP` from `ip route get 10.42.1.101`** and fails if
   there is no route. On a WiFi-only workstation this check will not pass as
   written — the documented path assumes the workstation is wired into the
   `10.42.1.0/24` network.

5. **Match the DDS settings exactly**: `ROS_DOMAIN_ID=4`,
   `RMW_IMPLEMENTATION=rmw_fastrtps_cpp`, and
   `FASTRTPS_DEFAULT_PROFILES_FILE` pointed at the rewritten `gdk_ros_domain.xml`.
   Note the variable name differs by distro — **Humble uses `FASTRTPS_…`**,
   **Kilted uses `FASTDDS_…`**.

6. **Clock synchronization is expected, not optional** — hence the PTP scripts.
   The robot is on `Asia/Shanghai (+0800)`; some boots recorded 1970 timestamps.

7. **Build messages from `deploy_gdk_msgs.sh` output**, not by hand. The repo's
   current single hand-placed `genie_msgs` package is missing its siblings and is
   not version-pinned to GDK 3.2.3.

---

## Appendix — access

```bash
# Credentials are deliberately not recorded here. Ask the robot's owner,
# or install an SSH key so no password is needed at all.
ssh <user>@<robot-ip>

source ~/app/env.sh                 # runtime env (LD_LIBRARY_PATH, PATH, PYTHONPATH)
source ~/app/gdk/scripts/ros_env.sh # ROS 2 + DDS env (restarts ros2 daemon)

curl http://192.168.1.224:8849/gdk_version   # version as JSON
# docs, installers and scripts are served from the same root
```
