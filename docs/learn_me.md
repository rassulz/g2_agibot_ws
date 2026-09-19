# Learning notes

Concepts behind the commands in this workspace, explained with the actual G2
in front of you. Written to be read in order, but each section stands alone.

Reference material: [`archtechture.md`](archtechture.md) for how the robot is
built, [`g2_info.md`](g2_info.md) for the raw system survey.

---

## 1. Why the robot needed a mode switch

The single most confusing thing about this robot:

> **The G2 does not speak ROS 2 by default.**

It runs AgiBot's own middleware (`cosine_bus` → `aorta`, carrying **protobuf**
messages). ROS 2 is an optional translation layer that only runs in the
`base-fastdds` launch scene.

This is why, before switching modes, you could see topic *names* but got no
data — the names came from participants that were registered, but nothing was
publishing.

**The symptom to remember:**

```
ros2 topic list          → topic appears
ros2 topic info <topic>  → Publisher count: 0     ← nobody is publishing
ros2 topic echo <topic>  → hangs forever
```

`Publisher count: 0` means the data source does not exist. Always check it
before debugging your own code.

---

## 2. What DDS actually is

ROS 2 has no network code of its own. It delegates everything to **DDS**, a
pub/sub standard. The implementation here is **Fast DDS**.

Three things follow from that:

### Discovery

Nodes find each other automatically. By default this is **multicast** — every
participant shouts on the local network. This is why the Docker container uses
`network_mode: host`: inside a bridged network, multicast never reaches your
LAN and nothing is ever discovered.

The G2 instead uses a **discovery server** — a single known address
(`10.42.1.101:11811`) that everyone registers with. More reliable on a complex
network, but it means you *must* supply a profile XML telling your client where
that server is. There is no automatic fallback.

### Domains

`ROS_DOMAIN_ID` partitions the network. Nodes on domain 4 cannot see nodes on
domain 0, even on the same wire. The G2 uses **domain 4** — a wrong domain
looks exactly like a broken network.

### QoS

Every publisher and subscriber carries a **Quality of Service** contract:
reliability (reliable vs best-effort), durability, history depth. **If the
publisher's and subscriber's QoS are incompatible, no data flows** — and
nothing errors out.

This produces the most baffling failure in ROS 2:

```
ros2 topic list   → works
ros2 topic type   → works
ros2 topic echo   → silent
```

Test with:

```bash
ros2 topic echo --qos-reliability best_effort /gdk/camera/head_color
```

Sensor data is usually `best_effort` (drop frames, stay current); commands and
state are usually `reliable`. `/gdk/joint_state` accepts both.

---

## 3. Workspaces, colcon, and sourcing

### The overlay model

ROS 2 layers environments. Each `source` adds packages on top of what came
before:

```
/opt/ros/kilted/setup.bash        ← underlay: ROS itself
    └── install/setup.bash        ← overlay: your packages
            └── another overlay   ← ...
```

Last one sourced wins. This is why the docs stress that *every new terminal*
needs the environment set up again — sourcing affects only the current shell.

### colcon

The build tool. From a workspace root containing `src/`:

```bash
colcon build                          # build everything
colcon build --packages-select foo    # just one package
colcon build --symlink-install        # edits to Python take effect without rebuild
```

It produces three directories:

| Directory | Contents |
|---|---|
| `build/` | intermediate objects, scratch |
| `install/` | the result — what you `source` |
| `log/` | build logs, useful when something fails |

All three are **generated**, never committed. They also cannot be shared
between ROS distros or architectures, which is why this workspace keeps them
per-distro (`build/kilted/`, `build/humble/`).

### Interface packages

`genie_msgs` and `gdk_msgs` contain no code — only `.msg` files, which are
*schema definitions*:

```
# gdk_msgs/msg/hal/JointState.msg
std_msgs/Header header
string[] name
float64[] position
float64[] velocity
float64[] effort
```

`colcon build` runs **rosidl**, which generates C++ headers and Python classes
from these. That is why building `genie_msgs` takes 3 minutes for 136 files —
it is generating and compiling thousands of lines per message.

It is also why message packages are **portable across distros but not across
architectures**: the `.msg` text is just text, but the generated `.so` files
are machine code.

---

## 4. Docker vs venv

You asked this, and it is worth writing down.

| | venv | Docker |
|---|---|---|
| Python packages | ✅ | ✅ |
| Python **version** | ❌ | ✅ |
| System libraries (glibc) | ❌ | ✅ |
| apt packages | ❌ | ✅ |
| Linux distro | ❌ | ✅ |
| Kernel | ❌ | ❌ (shares host's) |

A venv is a directory of Python packages plus a `PATH` trick. Everything below
Python is still the host's.

That is insufficient here because ROS 2 Kilted is *apt packages built for
Ubuntu 24.04*, compiled against glibc 2.39. Nothing in Python-land can provide
that on a 22.04 host. Docker replaces the entire userspace, so the container
genuinely *is* Ubuntu 24.04.

**What Docker does not change: the network.** The container uses your host's
interfaces and routes (`network_mode: host`). Docker changes the operating
system, not the cable.

Rough progression, lightest to heaviest:
**venv** (Python pkgs) → **conda** (+ some C libs) → **Docker** (userspace) →
**VM** (own kernel).

---

## 5. Why two containers

| Container | Ubuntu | ROS | Python | Use it for |
|---|---|---|---|---|
| `kilted` | 24.04 | Kilted | 3.12 | writing code that will **run on the robot** |
| `humble` | 22.04 | Humble | 3.10 | **watching/driving the robot** from your PC |

### `kilted` — matches the robot

Your deploy path is git: write here, push, pull on the robot, rebuild there.
Matching the distro means what compiles for you compiles there. ROS distros are
not source-compatible — `rclpy`/`rclcpp` APIs, QoS defaults and `rosidl` all
change between releases.

### `humble` — matches the GDK's workstation build

Two hard constraints, both discovered the hard way:

**1. The DDS profile is Fast DDS 2.x.** AgiBot's `gdk_ros_domain.xml` uses
`<discoveryServersList>` / `<RemoteServer>`, a schema Fast DDS 3.x (in Kilted)
removed:

```
XMLPARSER Error: Node 'discoveryServersList' without content
```

**2. The Python binding is `cpython-310`.** The file is literally named
`agibot_gdk.cpython-310-x86_64-linux-gnu.so`. A Python 3.12 interpreter does
not even consider that filename a candidate — you get `ModuleNotFoundError`,
not a load error.

### Reading ABI tags

A useful skill. `agibot_gdk.cpython-310-x86_64-linux-gnu.so` decodes as:

| Part | Meaning |
|---|---|
| `cpython-310` | built for CPython **3.10** |
| `x86_64` | Intel/AMD 64-bit |
| `linux-gnu` | Linux, glibc |

The robot's copy is `cpython-312-aarch64-linux-gnu.so` — different Python,
different CPU. Neither can substitute for the other.

Pure-Python wheels are tagged `py3-none-any` and work everywhere; that is why
`genie_msgs_pb-1.5.1-py3-none-any.whl` is portable while the binding is not.

---

## 6. Hands-on

Connect and watch the robot. Requires the robot in `base-fastdds` mode (§1).

```bash
cd /home/rassul/g2_agibot_ws
DDS_PROFILE_FILE=/home/dev/.cache/agibot/app/conf/dds/gdk_ros_domain.xml \
  docker compose -f docker/docker-compose.yml run --rm humble
```

Inside the container:

```bash
source ~/.cache/agibot/app/share/gdk_msgs/local_setup.bash
```

Then work through these:

```bash
# What exists?
ros2 topic list
ros2 topic list | grep '^/gdk'

# What type, and is anyone publishing?
ros2 topic info /gdk/joint_state
ros2 topic info -v /gdk/joint_state        # -v also shows QoS

# What does the type look like?
ros2 interface show gdk_msgs/msg/JointState

# How fast, and what is the data?
ros2 topic hz /gdk/joint_state             # expect ~100 Hz
ros2 topic echo --once /gdk/joint_state
ros2 topic bw /gdk/joint_state             # bandwidth

# Bigger data
ros2 topic hz /gdk/camera/head_color
ros2 topic hz /gdk/lidar/livox_front
```

### Exercise: a subscriber

Create `joint_listener.py`:

```python
import rclpy
from rclpy.node import Node
from gdk_msgs.msg import JointState

class JointListener(Node):
    def __init__(self):
        super().__init__('joint_listener')
        self.create_subscription(
            JointState, '/gdk/joint_state', self.on_joints, 10)

    def on_joints(self, msg):
        for name, pos in list(zip(msg.name, msg.position))[:3]:
            self.get_logger().info(f'{name}: {pos:.4f} rad')

def main():
    rclpy.init()
    rclpy.spin(JointListener())

if __name__ == '__main__':
    main()
```

```bash
python3 joint_listener.py
```

If it prints nothing, work the checklist in §7 — do not start editing the code.

---

## 7. Debugging checklist

When you see no data, go in this order. Each step rules out one layer.

| # | Check | Command | Failure means |
|---|---|---|---|
| 1 | Network | `ping 10.42.1.101` | cable / IP wrong |
| 2 | Robot mode | `ros2 topic info /gdk/joint_state` | `Publisher count: 0` → not in `base-fastdds` |
| 3 | Domain | `echo $ROS_DOMAIN_ID` | must be `4` |
| 4 | RMW | `echo $RMW_IMPLEMENTATION` | must be `rmw_fastrtps_cpp` |
| 5 | Profile | `echo $FASTRTPS_DEFAULT_PROFILES_FILE` | unset → no discovery server |
| 6 | Profile parses | watch for `XMLPARSER Error` | wrong container (Kilted) |
| 7 | Types | `ros2 interface show gdk_msgs/msg/JointState` | forgot to source `gdk_msgs` |
| 8 | QoS | `ros2 topic echo --qos-reliability best_effort ...` | QoS mismatch |
| 9 | Daemon stale | `ros2 daemon stop` | cached discovery state |

Step 9 is worth knowing: the ROS 2 daemon caches the graph. After changing
environment variables or robot modes, `ros2 topic list` can show stale results
until you restart it.

---

## 8. Vocabulary

| Term | Meaning |
|---|---|
| **DDS** | The pub/sub standard ROS 2 runs on. Here: Fast DDS. |
| **RMW** | ROS MiddleWare — the adapter between ROS and a DDS implementation |
| **QoS** | Per-endpoint delivery contract. Mismatches cause silent data loss. |
| **Domain** | Network partition ID. G2 uses 4. |
| **Discovery server** | Central registry replacing multicast discovery |
| **Participant** | One DDS process on the network |
| **colcon** | ROS 2 build tool |
| **ament** | The CMake/Python build system colcon drives |
| **rosidl** | Generates code from `.msg` / `.srv` files |
| **overlay / underlay** | Layered environments; last sourced wins |
| **HAL** | Hardware Abstraction Layer — `hal`, `hal_lowerlimb` |
| **WBC** | Whole-Body Control — coordinates all joints at once |
| **PNC** | Planning aNd Control — navigation and task execution |
| **SLAM** | Simultaneous Localization And Mapping |
| **DR** | Dead Reckoning — odometry from wheels/IMU |
| **aorta** | AgiBot's transport/discovery middleware |
| **cosine_bus** | AgiBot's pub/sub API layer |
| **EtherCAT** | Real-time fieldbus for motor control |
| **ABI** | Binary compatibility contract; why `cp310` ≠ `cp312` |
| **PREEMPT_RT** | Real-time Linux kernel patch — bounded latency |

---

## 9. Where to read more

- **The robot's own docs:** `http://10.42.1.101:8849/site/` — MkDocs, searchable,
  authoritative for GDK 3.2.3. More accurate than the public
  `support.agibot.com` pages, which cover 2.4.2.
- **Examples:** `~/.cache/agibot/app/gdk/examples/` — 8 C++, 14 Python, 2 ROS.
  `robot_demo.py` is the clearest introduction to the native API.
- **ROS 2 Kilted docs:** https://docs.ros.org/en/kilted/
- **Fast DDS:** https://fast-dds.docs.eprosima.com/ — especially discovery
  server and QoS sections.
