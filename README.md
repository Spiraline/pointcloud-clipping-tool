# PointCloud Clipper Tool


## Install
* Python 3.x
* ROS Melodic

```
sudo add-apt-repository ppa:sweptlaser/python3-pcl
sudo apt update
sudo apt install python3-pcl

pip3 install rospkg
pip3 install pyrosbag
pip3 install pycryptodome
pip3 install pycryptodomex
pip3 install python-gnupg
```

## Usage
```
python3 pcd_clipper -i=<input_rosbag_path>
```