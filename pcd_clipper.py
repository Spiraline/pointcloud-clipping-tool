import rosbag
import argparse
import os
import math

import rospy
from sensor_msgs.msg import PointCloud2, PointField
import sensor_msgs.point_cloud2 as pc2

import pcl
import struct
import ctypes

angle_above_y = 0
angle_below_y = 0
frame_id = "velodyne"

def isInside(y, x):
    if y >= 0:
        if angle_above_y == 0:
            return True
        else:
            return math.abs(math.degrees(math.atan(y / x))) > angle_above_y
    else:
        if angle_below_y == 0:
            return False
        else:
            return math.abs(math.degrees(math.atan(y / x))) < angle_below_y

def pcl_to_ros(pcl_array):
    ros_msg = PointCloud2()
    # ros_msg.header.stamp = rospy.Time.now()
    ros_msg.header.frame_id = frame_id

    ros_msg.height = 1
    ros_msg.width = pcl_array.size

    ros_msg.fields.append(PointField(
                            name="x",
                            offset=0,
                            datatype=PointField.FLOAT32, count=1))
    ros_msg.fields.append(PointField(
                            name="y",
                            offset=4,
                            datatype=PointField.FLOAT32, count=1))
    ros_msg.fields.append(PointField(
                            name="z",
                            offset=8,
                            datatype=PointField.FLOAT32, count=1))
    ros_msg.fields.append(PointField(
                            name="intensity",
                            offset=16,
                            datatype=PointField.FLOAT32, count=1))

    ros_msg.is_bigendian = False
    ros_msg.point_step = 32
    ros_msg.row_step = ros_msg.point_step * ros_msg.width * ros_msg.height
    ros_msg.is_dense = True
    buffer = []

    for data in pcl_array:
        s = struct.pack('>f', data[3])
        i = struct.unpack('>l', s)[0]
        pack = ctypes.c_uint32(i).value

        b = (pack & 0xFF000000) >> 24
        g = (pack & 0x00FF0000) >> 16
        r = (pack & 0x0000FF00) >> 8
        
        buffer.append(struct.pack('ffffBBBBIII', data[0], data[1], data[2], 1.0, 0, r, g, b, 0, 0, 0))

    ros_msg.data = b"".join(buffer)

    return ros_msg

def ros_to_pcl(rosmsg):
    points_list = []

    frame_id = rosmsg.header.frame_id

    for data in pc2.read_points(rosmsg, skip_nans=True):
        # Clip data
        if isInside(data[0], data[1]):
            points_list.append([data[0], data[1], data[2], data[3]])

    # pcl_data = pcl.PointCloud_PointXYZRGBA()
    pcl_data = pcl.PointCloud_PointXYZRGB()
    pcl_data.from_list(points_list)

    return pcl_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input file path', required=True)
    # parser.add_argument('--output', '-o', help='output file path', required=True)
    parser.add_argument('--angle', help='clipping angle deg (default = 180)', default=180)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print("File not exists : %s" % (args.input))
        exit(1)

    if args.input.split(".") == 1 or args.input.split(".")[-1] != 'bag':
        print("File should be rosbag file!")
        exit(1)
    
    if args.angle < 180:
        angle_above_y = (180 - args.angle) / 2
    elif args.angle > 180:
        angle_below_y = (args.angle - 180) / 2

    size = rosbag.Bag(args.input).get_message_count("/points_raw")
    idx = 0

    with rosbag.Bag("output.bag", 'w') as outbag:
        for topic, msg, t in rosbag.Bag(args.input).read_messages():
            pcl_data = ros_to_pcl(msg)
            outbag.write(topic, pcl_to_ros(pcl_data), t)
            idx = idx + 1
            print("\r[%d/%d] %.2f %% Complete" % (idx, size, idx*100/size), end="")
    print("")