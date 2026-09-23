# OmniHand O10 on the G2

How the left OmniHand O10 is driven, how to run it, and what is known about
why the robot does not detect it on its own.

**In short:** the robot's `hal` does not see this hand on CAN, so it is
invisible to the GDK and to the robot's ROS 2 bridge. The hand's own USB-C
port works, though. The `usb_hand` node drives the hand over that port and
exposes it on ROS 2.

---

## 1. Quick start

On the robot, in two terminals:

```bash
ssh agi@192.168.1.224
cd ~/g2_agibot_ws
```

**Terminal 1**, the driver. It keeps running until you press Ctrl+C:

```bash
src/omni_hand/scripts/hand_start.sh
```

**Terminal 2**, gestures:

```bash
src/omni_hand/scripts/hand.sh rock
src/omni_hand/scripts/hand.sh paper
src/omni_hand/scripts/hand.sh scissors
src/omni_hand/scripts/hand.sh neutral
src/omni_hand/scripts/hand.sh rock paper scissors neutral   # in order, 1 s apart
```

Each call prints the node's answer, e.g. `done rock (max error 0.012 rad)`.

> **The robot's e-stop does not stop this hand.** `usb_hand` drives it
> outside `hal`. To stop it, press Ctrl+C in terminal 1 or unplug the
> hand's USB-C.

---

## 2. Wiring

```
robot wrist ── U1: 24 V + CAN-FD ──┐
                                   ├── OmniHand O10 (left)
robot USB  ── hand's USB-C ────────┘
```

| Connector on the hand | Pins | Used for |
|---|---|---|
| **U1** WAFER-GH1.25-6PLB | 1 24V · 2 24V · 3 CAN_H · 4 CAN_L · 5 GND · 6 GND | power, and CAN-FD to the robot |
| **X1** GH125-S03CCA-00 | 1 RS485_A · 2 RS485_B · 3 GND | RS485, not used |
| **USB-C** | — | data only. It does not power the hand |

- **The hand draws power from U1 even when controlled over USB.** Keep U1
  connected.
- **Never plug or unplug U1 while the robot is on.** This is written in both
  the G2 manual ("End-effectors are NOT hot-swappable") and the O10 manual
  (§4.7). The USB-C cable can be plugged in while the hand is powered; that
  is the order the O10 manual gives.
- **LED on the back of the hand:** blue while initialising, then green when
  ready. If it stays blue, the supply voltage is outside 24 V ±10 %.

---

## 3. How it works

```
your code ──ROS 2──► usb_hand ──USB serial (460800 baud)──► hand controller
           "rock"               ee aa 01 00 15 08 … 1f 72
```

There are two layers:

- **ROS 2** carries messages between programs. Your code publishes `rock`
  and does not deal with bytes.
- **The hand's own binary protocol** runs between `usb_hand` and the hand.
  The node turns `rock` into frames the hand understands, using the AgiLink
  OmniHand SDK.

This mirrors how the rest of the robot works. The arm motors do not speak
ROS 2 either: `hal` drives them over EtherCAT/CAN, and the
`gdk_lumina_adapter` bridge republishes that as ROS 2 topics. For the hand,
`usb_hand` plays the part of both.

### ROS 2 interface

| Topic | Type | Direction |
|---|---|---|
| `/omni_hand/gesture` | `std_msgs/String` | in: `rock`, `paper`, `scissors`, `neutral`, or any O10 factory gesture |
| `/omni_hand/joint_state` | `sensor_msgs/JointState` | out: measured joint angles, 2 Hz |
| `/omni_hand/status` | `std_msgs/String` | out: `done …`, `dry run …`, `refused …`, `stopped …` |

From any ROS 2 program on the robot:

```bash
source src/omni_hand/scripts/hand_env.sh
ros2 topic pub --once /omni_hand/gesture std_msgs/msg/String "data: rock"
ros2 topic echo /omni_hand/status
ros2 topic echo /omni_hand/joint_state
```

`hand.sh` does the same, but it waits until `usb_hand` is subscribed before
sending. A bare `ros2 topic pub --once` can lose the message to discovery
latency.

### What a move does

1. Re-read the hand. Refuse to move if any joint reports `stalled`,
   `overheat`, `over_current`, `motor_except` or `commu_except`.
2. Clamp the target to the documented joint limits.
3. Split the move into a **thumb phase** and a **finger phase**, so that the
   thumb and fingers do not collide (`hand_model.o10_phases`):
   - fingers closing → fingers first, then the thumb wraps over them;
   - fingers opening → the thumb moves out of the way first, then the
     fingers.

   This comes from the hand itself: from rock to scissors, the index and
   middle fingers have to come out from under the thumb.
4. Ramp each phase from the measured pose. Then **wait until the hand has
   actually arrived** (within 0.05 rad, at most 2 s) before starting the
   next phase. If it has not arrived, stop with `stopped … did not reach`.
5. Finish with the SDK's `set_hand_gesture()` for the exact factory pose.
   `neutral` is our own pose, so it ends on the ramp instead.

---

## 4. Gestures

| Name | SDK pose | Look | Tested on the hand |
|---|---|---|---|
| `rock` | `fist2` | fist, thumb folded across the fingers | yes, within 0.02 rad |
| `paper` | `paper` | open palm | yes, within 0.013 rad |
| `scissors` | `num2` | index and middle straight and spread, thumb over ring and pinky | yes, within 0.013 rad |
| `neutral` | our own | hand at rest: fingers slightly curled, thumb beside the index | offline only |

`rock` uses `fist2` rather than `fist1`. In `fist1` the thumb sticks out
sideways, see `doc/pic/fist_1.jpg` and `fist_2.jpg` in the SDK.

`neutral` exists because none of the 18 factory poses is a resting hand:
`all_zero` is a flat hand, the same as paper. Its fingers are curled in a
cascade from index to pinky, 0.4 → 0.7 rad (23–40°), with no spread. It is
at least 0.69 rad of finger flexion from paper, 1.08 from rock and 1.15 from
scissors.

The other O10 factory gestures also work: `ok`, `like`, `ily`, `num1`,
`num3`, `num4`, `num6`, `num8`, `fist1`, `one_handed_finger_heart`,
`hand_heart1`–`3`, `clasping`, `all_zero`. Photos are in the SDK under
`doc/pic/`.

### Joint angles, left hand (rad)

Joint order is the same everywhere (SDK, GDK `end_reflection.json`, the
`joint_state` topic):

`thumb_roll · thumb_abad · thumb_mcp · index_abad · index_pip · middle_pip · ring_abad · ring_pip · pinky_abad · pinky_pip`

| | th roll | th abad | th mcp | idx abad | idx | mid | ring abad | ring | pinky abad | pinky |
|---|---|---|---|---|---|---|---|---|---|---|
| rock | -0.500 | 1.000 | -0.750 | 0 | 1.476 | 1.476 | 0 | 1.476 | 0 | 1.476 |
| paper | -0.580 | 0.210 | -0.001 | 0 | 0.015 | 0.015 | 0 | 0.015 | 0 | 0.015 |
| scissors | -0.480 | 1.500 | -0.790 | 0.160 | 0.015 | 0.015 | 0 | 1.476 | 0 | 1.476 |
| neutral | -0.300 | 0.350 | -0.200 | 0 | 0.400 | 0.500 | 0 | 0.600 | 0 | 0.700 |

The factory poses were taken from the SDK's offline kinematics solver
(`src/omni_hand/tools/dump_gestures.py`), not measured or guessed. On the
right hand the thumb and abduction signs are mirrored.

---

## 5. Options

### `hand_start.sh`

```bash
src/omni_hand/scripts/hand_start.sh                  # motors' own speed (steps:=1)
src/omni_hand/scripts/hand_start.sh --dry-run        # answer gestures, do not move
src/omni_hand/scripts/hand_start.sh -p steps:=10     # slow: ~2 s per phase
src/omni_hand/scripts/hand_start.sh -p steps:=5 -p step_delay:=0.1
```

It refuses to start a second driver, because two processes on one serial
port would fight over the hand. Arguments after `--dry-run` go to the node
as ROS parameters, and they win over the script's `steps:=1` because ROS
takes the last value of a repeated parameter.

| Parameter | Default | Meaning |
|---|---|---|
| `enable` | `true` from `hand_start.sh`, `false` in the node | `false` = dry run |
| `steps` | `1` from `hand_start.sh`, `10` in the node | ramp steps per phase |
| `step_delay` | `0.2` | seconds per ramp step |
| `state_rate` | `2.0` | Hz for `/omni_hand/joint_state`; `0` turns it off |
| `side` | `left` | `left` or `right` |
| `port` | `/dev/serial/by-id/usb-STMicroelectronics_STM32_Virtual_ComPort_386133553335-if00` | stable name, survives reboots |

Time per phase is about `steps × step_delay`, plus the time the hand needs
to physically arrive. There are two phases per gesture. `steps:=1` jumps
straight to the target at the motors' own speed, as AgiBot's demo does.

### `hand.sh`

```bash
src/omni_hand/scripts/hand.sh rock paper scissors            # 1 s between gestures
src/omni_hand/scripts/hand.sh --pause 3 rock paper scissors  # other pause
```

The pause counts from the moment the previous gesture is done. The script
exits non-zero if a gesture was refused, stopped, or not answered within
20 s.

---

## 6. One-time setup on the robot

This is already done on this robot and is listed here for a fresh one.
Nothing is installed system-wide.

```bash
cd ~/g2_agibot_ws && git pull

# AgiLink SDK, unpacked rather than installed (the wheel carries all its libraries)
git clone https://github.com/AgibotTech/agillink_omnihand_sdk ~/agillink_omnihand_sdk
cd ~/agillink_omnihand_sdk/linux/aarch64/python
mkdir -p ~/omnihand_pkg && python3 -m zipfile -e \
    omnihand-1.1.8-cp312-cp312-linux_aarch64.whl ~/omnihand_pkg

# serial port access for user agi (then log in again)
sudo usermod -aG dialout agi
```

`colcon` is not needed: the scripts run the node straight from the checkout.

**Do not run the SDK's `install.sh` on the robot.** It deletes and replaces
`/usr/local/lib/libusb-1.0.so*` and pip-installs into the robot's system
Python with `--break-system-packages`. **Do not run `setup_socketcan.sh`**
either: without arguments it reconfigures every `canN`, including the arm
buses.

---

## 7. The hand

Read over USB (`0xCD`, `0xC2`, `0x02`, `0x0D`):

| | |
|---|---|
| Model | O10, 10 active DOF |
| Revision | **T1** |
| Firmware | **1.2.3** (latest on AgiBot's site: 1.2.14) |
| Hardware | 3.0.0 |
| Serial | B985CUUAM2603241031 (made 2026-03-24) |
| USB device | `0483:5740` STMicroelectronics Virtual COM Port, `cdc_acm` |

**Firmware has deliberately not been updated.** Revision T1 is a hardware
stage, and a firmware update is unlikely to change how the robot treats it
(see §8). Confirm with AgiBot before flashing anything.

### Protocol notes

Frame: `EE AA | ID (LE, 01 00) | length | CMD | data | CRC16`, where CRC is
CRC-16/XMODEM (poly 0x1021, init 0) over everything before it. This was
verified against captured frames.

| CMD | Meaning | Used by |
|---|---|---|
| `0x08` | set all 10 motor positions (0–4096, LE) | every move, including `set_hand_gesture()` |
| `0x09` | read all positions | SDK `init()` |
| `0x0D` | read error code | SDK `init()` |
| `0x02` | read enable state | diagnostics |
| `0xCD` | model, revision, versions | diagnostics |
| `0xC2` | serial number | diagnostics |

The hand has no "gesture" command: the SDK computes motor positions and
sends `0x08`. In this SDK, `init()` is what re-reads the hand, and the
getters return cached values. The node calls `init()` whenever it needs
fresh data. `get_device_info()` over USB returns placeholders (ID 1,
125 kbps), not the hand's CAN settings, so do not trust it.

---

## 8. Why the robot does not detect it

What was checked, over four boots (`boot00000062`, `63`, `65`, `66`) with two
different O10 units:

- **hal asks and gets nothing.** At every boot, `hal` sends
  `GetProducerInfo frame.id 0x81010101` and `GetSoftwareVersion 0x84010101`
  and receives only `recv frame.id 0x0`. Then:
  ```
  hand_deduce_tool.cpp:247]  Cannot find producer , use unknow
  uniform_picker_wrapper.cpp:371]  invalid hand_tool
  ```
  In `boot00000062`, an OmniPicker on the right wrist answered
  `frame.id 0x301` and was detected at once. So the detection path itself
  works.
- hal uses `interface_ can` with `control_id 512` for the left hand (513 for
  the right), and its configs are
  `/home/agi/app/conf/hal/uniform_left_config.yaml` and
  `uniform_right_config.yaml`.
- **GDK:** `left_end_model = ''`, `left_end_error = 2147549184`
  (`0x80010000`), and `get_end_state()` returns "No end state message
  found".
- **Ruled out:**
  - power: the LED is green;
  - hot-plugging: the hand was connected with the robot off;
  - bus timing: the robot's CAN-FD controllers run 1 Mbps @ 0.8 /
    5 Mbps @ 0.75, exactly what the hand requires;
  - bus health: all controllers are `ERROR-ACTIVE` with zero errors;
  - wrong connector: U1 is the CAN-FD one;
  - a faulty unit: two units behaved the same.
- **Robot CAN interfaces:** `can0` and `can1` carry traffic (the arms).
  `can2` and `can4` are configured but idle. `can3` and `can5` are `vcan`.
  **Do not bring any of them down.**

**Leading hypothesis:** the robot's GDK only knows this hand as **`o10_t2`**,
and the hand reports revision **T1**. The O10 manual says the CAN side
answers standard CAN-FD frames on node ID `0x09` by default, while hal's
query IDs look like extended frames. Either difference would produce exactly
this silence. This is unconfirmed.

**Question for AgiBot:** does the G2 support O10 revision T1, and if so,
which CAN ID, frame format and configuration must the hand present on the
wrist bus?

Once hal detects the hand, the GDK path in this package takes over and the
robot's e-stop covers the hand again: `hand_identify.py` reads it,
`hand_grasp.py` commands it through `move_ee_pos()`.

---

## 9. Troubleshooting

| Message | Cause | Fix |
|---|---|---|
| `usb_hand is not running -- start it with hand_start.sh` | no driver in this ROS 2 environment | start terminal 1. Always use the scripts, so that both sides share one environment |
| `… does not exist -- is the hand USB-C plugged into the robot?` | no serial port | plug in the USB-C; check `ls /dev/serial/by-id/` |
| `no permission on …` | not in `dialout` | `sudo usermod -aG dialout agi` and log in again, or `sudo chmod 666 /dev/ttyACM0` until the next replug |
| `cannot import the AgiLink SDK` | `~/omnihand_pkg` missing | see §6 |
| `usb_hand is already running` | a driver is already up | use it, or stop it first |
| `refused …: joint faults [(5, 'stalled')]` | a motor reported a fault | check nothing blocks the fingers; restart the driver |
| `stopped … did not reach it in 2 s` | the hand did not get to a phase target | something is in the way, or the move is too fast; try `-p steps:=10` |
| `refused '…': unknown gesture` | typo | the message lists every known name |
| GDK node segfaults on the PC with `aorta … 127.0.0.1:2379 fail` | the PC is not on the robot's `10.42.1.*` Ethernet | this only affects GDK nodes on the PC; `usb_hand` runs on the robot |
| the node ignores changes after `git pull` | a running process keeps old code | Ctrl+C and start it again |

---

## 10. Files

| Path | What |
|---|---|
| `src/omni_hand/omni_hand/usb_hand.py` | the USB driver node |
| `src/omni_hand/omni_hand/hand_cmd.py` | gesture client behind `hand.sh` |
| `src/omni_hand/omni_hand/hand_model.py` | joint names, limits, gestures, `neutral`, phase planner |
| `src/omni_hand/scripts/hand_start.sh`, `hand.sh`, `hand_env.sh` | launchers; `hand_env.sh` is the shared environment |
| `src/omni_hand/tools/dump_gestures.py` | regenerates the factory gesture tables from the SDK solver |
| `src/omni_hand/omni_hand/hand_identify.py`, `hand_grasp.py` | GDK path, for when hal detects the hand |

## 11. References

- [OmniHand O10 manual, 2026-01](https://www.zhiyuan-robot.com/file/ueditor/php/upload/file/20260108/1767856819296879.pdf): pinout, CAN-FD and USB protocol, LED, hot-plug rule
- [OmniHand O10 downloads](https://www.zhiyuan-robot.com/DOCS/OS/Omnihand-O10): firmware, OmniHand Toolbox (Windows)
- [AgiLink OmniHand SDK](https://github.com/AgibotTech/agillink_omnihand_sdk): `doc/en/QUICK_START.md`, `TROUBLESHOOTING.md`, `API_PYTHON_O10.md`, `API_KINEMATICS_PYTHON_O10.md`
- [AGIBOT G2 user manual](https://www.agibot.com/filepage/296.html) §2.5: wrist connector, end effectors not hot-swappable
- [`learn_me.md`](learn_me.md) §6: why GDK nodes need the robot's Ethernet
