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

Some sensors create a `/dev` symlink on the host after the udev rule is installed, for example:

| Sensor value | Host `/dev` path |
|--------------|-----------------|
| `ydlidar` | `/dev/ydlidar` |
| `ld06`, `ld19`, `stl27l` | `/dev/ldlidar` |
| `a1`, `a2`, `a3`, ... | `/dev/rplidar` |

Use this path when mapping the device in `docker-compose.yaml` (see step 6).

### 4. Reload udev rules

After installing, apply the rules without rebooting:

```bash
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### 5. Verify the device symlink

Plug in the sensor, then confirm the udev symlink exists on the host:

```bash
ls /dev/<sensor_name>
# Example:
ls /dev/ldlidar
```

### 6. Update the bringup service devices

Edit `docker/docker-compose.yaml` and update the `bringup` service's `devices` section
to map the correct host device into the container:

```yaml
  bringup:
    ...
    devices:
      - /dev/ldlidar:/dev/ldlidar
```

### 7. Run the robot

```bash
docker compose up bringup
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

To stop the simulation, stop any process by pressing Ctrl + C and run:
```
tmuxinator stop sim
```
