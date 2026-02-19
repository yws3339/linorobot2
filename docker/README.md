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

**Microcontroller:**

Plug in the microcontroller (for example Raspberry Pi Pico), then confirm the device node exists on the host:

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
| Raspberry Pi Pico microcontroller | `/dev/ttyACM0` |
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
      - /dev/ttyACM0:/dev/ttyACM0 # Robot's microcontroller (e.g. Pico)
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

### 1. Configure docker/.env for simulation

Edit `docker/.env` and set the `BASE_IMAGE` variable to select the simulation environment:

```
BASE_IMAGE=gazebo        # Standard Gazebo simulation
BASE_IMAGE=gazebo-cuda   # Gazebo with CUDA support (recommended for machines with an NVIDIA GPU)
```

#### gazebo-cuda

The `gazebo-cuda` image enables CUDA support for Gazebo on machines equipped with an NVIDIA GPU. Gazebo is a graphics-intensive simulator — it renders 3D environments, lighting, and sensor data in real time. Running it on a GPU offloads the heavy rendering workload from the CPU, resulting in smoother simulation with higher frame rates and more stable physics-rendering synchronization, particularly when using depth sensors or camera plugins that produce large visual outputs.

#### VirtualGL

Since the default Docker setup is assumed to be **headless** (no physical display attached), the `gazebo-cuda` image also runs **VirtualGL**, which intercepts OpenGL calls from Gazebo and redirects them to the GPU for hardware-accelerated rendering. Without VirtualGL on a headless server, Gazebo would fall back to software rendering, negating the benefits of the GPU entirely.

#### Headless setup and cloud simulation

The headless setup allows the simulation to run on remote servers or cloud instances such as **GCP** or **AWS**, where no monitor is physically connected. The rendered display is forwarded to display `:200`, where a VNC server captures it and streams it to a web-based VNC client accessible from a browser at `http://<host_ip>:3000`.

This approach is advantageous in two ways:

- **Cloud simulation**: The entire simulation stack — Gazebo, Nav2, and sensor processing — runs on a remote server. The browser becomes the only local interface needed, with no requirement for a local ROS installation or display.

- **Efficient remote visualization**: In a traditional setup, tools like RViz on a remote machine receive raw topic data (e.g. point clouds, laser scans) over the network, which can be highly bandwidth-intensive. With VNC, only the compressed video stream of the rendered display is transmitted — significantly reducing network usage, especially for data-heavy sensors like 3D LiDARs or RGBD cameras.

---

### 2. Install Tmuxinator

Follow the installation instructions for Tmuxinator [here](https://github.com/tmuxinator/tmuxinator?tab=readme-ov-file#installation)

### 3. Running the demos using Tmuxinator and Docker

#### 3.1. First, export the tmuxinator project path:

```
cd linorobot2/docker/demos
export TMUXINATOR_CONFIG=$PWD
```

#### 3.2. Running the Nav2 demo in Gazebo:

```
tmuxinator start sim
```

Once running, visualization is available at: `http://<host_ip>:3000`

To stop the simulation, stop any process by pressing Ctrl + C and run:
```
tmuxinator stop sim
```
