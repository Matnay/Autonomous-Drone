# Autonomous-Drone
A detailed repository with step-by-step instructions on implementing an autonomous drone:
All algorithms can be simulated on the px4 SITL simulator using Gazebo.
![Image EXAMPLE RESULT](https://github.com/Matnay/Autonomous-Drone/blob/master/Screenshot%20from%202019-06-30%2018-54-35.png)
https://github.com/PX4/sitl_gazebo

STEP 1:
installation of mavros

Install all dependencies

```
sudo apt install -y \
	ninja-build \
	exiftool \
	python-argparse \
	python-empy \
	python-toml \
	python-numpy \
	python-yaml \
	python-dev \
	python-pip \
	ninja-build \
	protobuf-compiler \
	libeigen3-dev \
	genromfs

pip install \
	pandas \
	jinja2 \
	pyserial \
	cerberus \
	pyulog \
	numpy \
	toml \
	pyquaternion
```

* Create a new workspace:	
```	
mkdir -p ~/catkin_ws/src
```
and run the following commands:
```
cd ~/catkin_ws
catkin init && wstool init src

rosinstall_generator --rosdistro kinetic mavlink | tee /tmp/mavros.rosinstall
rosinstall_generator --upstream mavros | tee -a /tmp/mavros.rosinstall

wstool merge -t src /tmp/mavros.rosinstall
wstool update -t src -j4
rosdep install --from-paths src --ignore-src -y

sudo ./src/mavros/mavros/scripts/install_geographiclib_datasets.sh
sudo apt install ros-kinetic-catkin python-catkin-tools
catkin build

cd ~/catkin_ws/src
git clone https://github.com/PX4/Firmware.git
cd Firmware
git checkout v1.8.0
make posix_sitl_default gazebo
```

* Open a new terminal and type:
```
sudo gedit ~/.bashrc
```
* Add the following lines to the file that opens:
```
source ~/catkin_ws/devel/setup.bash
source ~/catkin_ws/src/Firmware/Tools/setup_gazebo.bash ~/catkin_ws/src/Firmware/ ~/catkin_ws/src/Firmware/build/posix_sitl_default
export ROS_PACKAGE_PATH=ROS_PACKAGE_PATH:~/catkin_ws/src/Firmware
export ROS_PACKAGE_PATH=ROS_PACKAGE_PATH:~/catkin_ws/src/Firmware/Tools/sitl_gazebo
```
* Create a new workspace and copy the codes into the 'src' directory
* Run the scripts by
```
cd <workspace_name>
source devel/setup.bash
rosrun <package_name> <script_name.py>
```
Navigator.py - Path planning, SLAM and stereo camera based obstacle avoidance

A link to the videos showing final results can be found here:
https://drive.google.com/drive/u/0/folders/1qhfXiX-CNiFpI8fsTxjDEUSapS3mkc9u
