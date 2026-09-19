# AgiBot G2 — System Architecture

How the robot is put together, and where your code plugs in.

Everything here was verified against the physical robot (GDK 3.2.3,
`10.42.1.101`). Facts that were inferred rather than observed are marked.

Companion documents: [`g2_info.md`](g2_info.md) for the raw system survey,
[`learn_me.md`](learn_me.md) for the concepts behind the terminology.

---

## 1. The big picture

The G2 does **not** run on ROS 2. It runs AgiBot's own middleware, and ROS 2 is
an optional bridge layered on top.

```
┌──────────────────────────────────────────────────────────────┐
│  ROBOT — Jetson AGX Thor, Ubuntu 24.04, PREEMPT_RT kernel     │
│                                                              │
│   ┌────────────────────────────────────────────────────┐     │
│   │ Application layer                                  │     │
│   │  taskflow · skills · navigation · voice · HMI      │     │
│   └───────────────────────┬────────────────────────────┘     │
│                           │                                  │
│   ┌───────────────────────▼────────────────────────────┐     │
│   │ Control layer                                      │     │
│   │  pnc (planning)  ·  wbc (whole-body control)       │     │
│   │  slam  ·  dr (dead reckoning)  ·  arbitrator       │     │
│   └───────────────────────┬────────────────────────────┘     │
│                           │                                  │
│   ┌───────────────────────▼────────────────────────────┐     │
│   │ HAL — hal, hal_lowerlimb, camera_service, lidar    │     │
│   └───────────────────────┬────────────────────────────┘     │
│                           │                                  │
│         EtherCAT (motors) │ CAN │ PCIe │ MIPI (cameras)      │
└───────────────────────────┼──────────────────────────────────┘
                            │
             ┌──────────────▼──────────────┐
             │  cosine_bus  →  aorta       │   ← native middleware
             │  protobuf messages          │      (default)
             └──────────────┬──────────────┘
                            │
                  ┌─────────▼─────────┐
                  │   Fast DDS 3.2.2  │   ← transport
                  └─────────┬─────────┘
                            │
        ════════════════════▼════════════════════  10 GbE
                    ROS 2 bridge (optional)
                      /gdk/*  topics
```

**Key consequence:** in its default mode the robot publishes *nothing* to ROS 2.
You must switch modes first — see §5.

---

## 2. Middleware layers

| Layer | What it is | Where it shows up |
|---|---|---|
| **aorta** | AgiBot's transport/discovery service. Centralized discovery over HTTP at `10.42.1.101:2379`. | `AORTA_URI`, `AORTA_DISCOVERY_URI`, `aorta.service` |
| **cosine_bus** | Pub/sub API the applications are written against. Pluggable backend. | `COSINE_BUS_DEFAULT_MIDDLEWARE=aorta` |
| **protobuf** | The message encoding — *not* ROS IDL. protobuf 28.3. | `gdk/lib/*_pb/` Python packages |
| **Fast DDS** | The wire protocol underneath. Version 3.2.2. | `conf/dds/*.xml` |
| **ROS 2 bridge** | Optional translation to ROS topics and IDL. | `gdk/config/ros_bridge_config.json` |

The applications talk **cosine_bus**, which by default dispatches through
**aorta**. Both ultimately ride **Fast DDS**. ROS 2 is bolted on at the edge.

This is why `import agibot_gdk` tries to reach `127.0.0.1:2379` and fails from a
workstation — it is looking for aorta, not for ROS.

---

## 3. Discovery

The robot runs a **Fast DDS discovery server**, not the default multicast
discovery:

```
fast-discovery-server-1.0.1 42 -i 0 -l 10.42.1.101 -q 11811 -p 11811
```

| Property | Value |
|---|---|
| Address | `10.42.1.101:11811` (binds `0.0.0.0`, verified) |
| Server ID | `0` |
| ROS domain | **4** |
| RMW | `rmw_fastrtps_cpp` |

Clients find it through the profile XML, not through multicast. That is why a
workstation cannot see anything without `FASTRTPS_DEFAULT_PROFILES_FILE` set.

---

## 4. Networks

The robot is heavily multi-homed. Each bus has a job.

| Interface | Address | Purpose |
|---|---|---|
| `xfi2.10g@mgbe2_0` | **10.42.1.101/24** | 10 GbE — main bus, discovery, GDK. **Plug your workstation in here.** |
| `wlan0` | 192.168.1.224/24 | WiFi — SSH and HTTP only, *not* viable for DDS |
| `ecat0/1/2@mgbe1_0` | — | EtherCAT — motor control, hard real-time |
| `can0`–`can5` | — | CAN — sensors, power, chassis |
| `xfi0.20 / .60 / .80` | 10.42.0.x, 10.42.80.x | internal subsystem VLANs |
| `pad` | 10.42.6.101/24 | tablet link |

**Workstation must be `10.42.1.102/24`, wired directly.** This is what the GDK
docs specify, and `ros_env.sh` derives `DEV_IP` from the route to
`10.42.1.101`.

WiFi does not work for DDS even though the discovery port answers: the robot's
data-plane participants bind to `10.42.x.x` interfaces that are unreachable
from a WiFi client.

---

## 5. Launch scenes (modes)

The robot runs one "scene" at a time — a set of processes defined in
`~/app/conf/manifest.d/*.json`. Switched with `~/app/bin/mode_switch`.

| Scene | Purpose |
|---|---|
| `base` | **Default.** Normal operation. No ROS 2 output. |
| **`base-fastdds`** | **Enables the ROS 2 bridge.** Required for `/gdk/*` topics. |
| `base-remote` | Remote/teleoperation |
| `base-rl` | Reinforcement-learning control |
| `base-o10` | Variant configuration |
| `develop` | Development |
| `idle` | Minimal |

```bash
source ~/app/env.sh
~/app/bin/mode_switch --mode base-fastdds   # enable ROS 2
~/app/bin/mode_switch --mode base           # back to default
```

The setting is not persistent — a reboot returns the robot to
`DEFAULT_LAUNCH_SCENE=base` from `conf/sys/run.conf`.

---

## 6. Message packages

Thirteen ROS interface packages ship in `~/app/ros_msg/`. They are **not**
interchangeable, and picking the wrong one is the most common source of
"message type is invalid".

| Package | Msgs | Role |
|---|---:|---|
| **`gdk_msgs`** | 29 | **The public API.** Types on `/gdk/*`. This is what your code should use. |
| `genie_msgs` | 136 | Robot-internal interfaces, behind the bridge |
| `aimdk_msgs` | 76 | Types on `/lumina/*` and `/aima/*` (application layer) |
| `hmi_msgs` | 151 | Face screen / HMI |
| `rh_msgs_v4` | 129 | Robot hardware v4 |
| `pnc_msgs` | 44 | Planning & control |
| `rh_msgs` | 43 | Robot hardware |
| `mc_msgs`, `dlb_msgs` | 13 each | Motion control; data logging |
| `monitor_msgs` | 11 | System health telemetry (**not** the face screen) |
| `gma_msgs` | 10 | — |
| `proto2ros` | 7 | protobuf↔ROS conversion primitives |
| `fsm_msgs` | 6 | State machine |

A **prebuilt** `gdk_msgs` ships at `~/.cache/agibot/app/share/gdk_msgs/` — source
its `local_setup.bash` rather than compiling your own.

### `gdk_msgs` contents

```
common/          CommonRequest, CommonResponse
hal/             JointState, WholeBodyStatus
interaction/     AsrText, VideoDisplay
motion_control/  EndEffectorPoseControl, JointPositionRequst,
                 JointPositionServo, MotionControlStatus
pnc/             NormalNavigation*, NormalNaviPathCost*, Task{Cancel,Pause,Resume}*,
                 TaskHeader, TaskServiceResult, TaskState
slam/            GuidePtInfo, HmiMap, HmiMapInfo, MapInfo, OdomInfo, PolygonInfo
```

---

## 7. The ROS 2 bridge

`gdk/config/ros_bridge_config.json` maps internal topics into the `/gdk/*`
namespace, translating protobuf types to ROS IDL as it goes.

| Internal topic | | `/gdk/*` topic |
|---|---|---|
| `/hal/joint_state` | → | `/gdk/joint_state` |
| `/wbc/motion_control_status` | → | `/gdk/motion_control_status` |
| `/MotionControlService/JointPosition/response` | → | `/gdk/joint_pos_response` |
| `/gdk/joint_pos_request` | → | `/MotionControlService/JointPosition/request` |
| `/gdk/joint_control` | → | `/wbc/joint_control` |

Read the arrows carefully: **state flows outward, commands flow inward.** You
subscribe to `/gdk/joint_state` and publish to `/gdk/joint_pos_request`.

### Topics available in `base-fastdds` mode

19 `/gdk/*` topics, verified live:

```
/gdk/joint_state              100 Hz, gdk_msgs/msg/JointState   (verified)
/gdk/motion_control_status
/gdk/joint_pos_request        /gdk/joint_pos_response
/gdk/joint_control            /gdk/joint_control_low_delay
/gdk/odom_info                /gdk/tf
/gdk/camera/head_color        /gdk/camera/head_depth
/gdk/camera/head_stereo_left  /gdk/camera/head_stereo_right
/gdk/camera/hand_left_color   /gdk/camera/hand_right_color
/gdk/lidar/livox_front        /gdk/lidar/livox_back
/gdk/imu/chassis              /gdk/imu/livox_front  /gdk/imu/livox_back
```

There are also `/lumina/*`, `/aima/*`, `/voice/*` and `/face_ui/*` topics
(≈62 total). Those belong to the application layer and use `aimdk_msgs` types;
they are visible but are not the documented API.

---

## 8. The two access paths

The GDK offers two ways in. They are independent.

```
        ┌─────────────────────────┐        ┌──────────────────────────┐
        │  Native GDK API         │        │  ROS 2 bridge            │
        ├─────────────────────────┤        ├──────────────────────────┤
        │ C++  libgdk_adapter.so  │        │ /gdk/* topics            │
        │ Py   import agibot_gdk  │        │ gdk_msgs types           │
        ├─────────────────────────┤        ├──────────────────────────┤
        │ speaks aorta/protobuf   │        │ needs base-fastdds mode  │
        │ needs aorta reachable   │        │ standard rclpy / rclcpp  │
        │ Python 3.10 (x86_64)    │        │ any ROS 2 ≥ Humble       │
        └─────────────────────────┘        └──────────────────────────┘
```

Use the ROS bridge for ordinary robotics work. Use the native API for features
the bridge does not expose (skills, maps, some interaction calls).

---

## 9. Where your code runs

Two distinct setups, easy to confuse:

### A. Code deployed to the robot

```
workstation (x86_64)                      robot (aarch64)
docker: kilted                            Ubuntu 24.04 / Kilted
write + build + commit  ──push──▶ git ──pull──▶  colcon build + run
```

The `kilted` container matches the robot's Ubuntu, ROS distro and Python, so
what compiles on the workstation compiles on the robot. Architectures differ —
only **source** crosses; `build/` and `install/` are regenerated on each side.

### B. Workstation observing or driving the robot

```
workstation 10.42.1.102  ──10 GbE──▶  robot 10.42.1.101:11811
docker: humble                        Fast DDS discovery server
```

Must be the `humble` container. Two verified reasons:

1. `conf/dds/gdk_ros_domain.xml` uses the Fast DDS **2.x** XML schema
   (`<discoveryServersList>`/`<RemoteServer>`). Fast DDS 3.x in Kilted rejects
   it: `XMLPARSER Error: Node 'discoveryServersList' without content`.
2. The shipped Python binding is `agibot_gdk.cpython-310-...so` — Python 3.12
   cannot load it.

---

## 10. Software stack

Selected components from `~/app/.pkg_version` (full list in
[`g2_info.md`](g2_info.md#10-software-stack-from-pkg_version)):

**AgiBot:** `agibot_gdk 3.2.3` · `aorta 2.2.0` · `cosine_bus 3.7.0` ·
`hal rc-2.2.13-3` · `motion-control 0.5.34` · `navigation 1.2.7` · `slam 1.1.18`

**Robotics:** Pinocchio 3.3.0 (rigid-body dynamics) · GTSAM 4.2 (factor-graph
SLAM) · FCL 0.7.0 (collision) · nlopt 2.7.1 · qpOASES 3.2.1 (QP control) ·
BehaviorTree.CPP 4.6.2 · octomap · PCL 1.13.1

**Infrastructure:** Fast DDS 3.2.2 · protobuf 28.3 · gRPC 1.70.0 · OpenCV 4.13.0

The presence of Pinocchio + qpOASES + FCL indicates QP-based whole-body control
with collision avoidance; GTSAM indicates factor-graph SLAM. *(Inference from
dependencies, not from reading the control code.)*

---

## 11. Reference

| | |
|---|---|
| Robot internal IP | `10.42.1.101` |
| Workstation IP | `10.42.1.102` (static, wired) |
| Discovery server | `10.42.1.101:11811` |
| aorta discovery | `http://10.42.1.101:2379` |
| GDK docs (MkDocs) | `http://10.42.1.101:8849/site/` |
| GDK downloads | `http://10.42.1.101:8849/` |
| ROS domain | `4` |
| RMW | `rmw_fastrtps_cpp` |
| GDK version | 3.2.3, commit `1802ca1` |
