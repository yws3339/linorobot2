## Hardware

### 1. Configure for hardware

Edit `docker/.env` and set:

```
BASE_IMAGE=hardware
ROBOT_BASE=<robot_type>      # 2wd, 4wd, or mecanum
LASER_SENSOR=<laser_sensor>  # e.g. ld06, a1, ydlidar  (leave blank if not used)
DEPTH_SENSOR=<depth_sensor>  # e.g. realsense, oakd     (leave blank if not used)
```

### 2. Build the image

```bash
cd linorobot2/docker
docker compose build
```

### 3. Install udev rules on the host

The Docker image already contains the sensor drivers (installed during build). To create
the `/dev/<sensor>` symlinks on the **host** machine, run `install.bash` with `--udev-only`.

**`--udev-only` is required** — it forces the script to only copy udev rules and skip
driver installation (which is not needed since drivers are already inside the container).

```bash
# From the linorobot2 repo root on the host:
bash install.bash --laser <laser_sensor> --udev-only
# and/or
bash install.bash --depth <depth_sensor> --udev-only
```

### 4. Reload udev rules

After installing, apply the rules without rebooting:

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 5. Verify the device symlinks

**Microcontroller (Teensy):**

Plug in the Teensy, then confirm the device node exists on the host:

```bash
ls /dev/ttyACM0
```

**Sensors:**

Plug in the sensor, then confirm the udev symlink exists on the host:

```bash
ls /dev/<sensor_name>
# Examples of possible names:
# /dev/ydlidar   (ydlidar)
# /dev/ldlidar   (ld06, ld19, stl27l)
# /dev/rplidar   (a1, a2, a3, ...)
```

Some sensors create a `/dev` symlink on the host after the udev rule is installed:

| Device | Host `/dev` path |
|--------|-----------------|
| Teensy microcontroller | `/dev/ttyACM0` |
| `ydlidar` | `/dev/ydlidar` |
| `ld06`, `ld19`, `stl27l` | `/dev/ldlidar` |
| `a1`, `a2`, `a3`, ... | `/dev/rplidar` |

### 6. Update the bringup service devices

Edit `docker/docker-compose.yaml` and update the `bringup` service's `devices` section
to map the correct host devices into the container:

```yaml
  bringup:
    ...
    devices:
      - /dev/ttyACM0:/dev/ttyACM0 # Robot's microcontroller (e.g. Teensy)
      - /dev/ldlidar:/dev/ldlidar # Laser sensor (adjust to match your sensor symlink)
```

### 7. Run the robot

```bash
cd linorobot2/docker/demos
export TMUXINATOR_CONFIG=$PWD
tmuxinator start hardware
```

Once running, visualization is available at: `http://<robot_ip>:3000`

To stop, press Ctrl + C in any pane and run:

```bash
tmuxinator stop hardware
```

---

## Simulation

### 1. Install Tmuxinator

Follow the installation instructions for Tmuxinator [here](https://github.com/tmuxinator/tmuxinator?tab=readme-ov-file#installation)

### 2. Running the demos using Tmuxinator and Docker

#### 2.1. First, export the tmuxinator project path:

```
cd linorobot2/docker/demos
export TMUXINATOR_CONFIG=$PWD
```

#### 2.2. Running the Nav2 demo in Gazebo::

```
tmuxinator start sim
```

Once running, visualization is available at: `http://<host_ip>:3000`

To stop the simulation, stop any process by pressing Ctrl + C and run:
```
tmuxinator stop sim
```
