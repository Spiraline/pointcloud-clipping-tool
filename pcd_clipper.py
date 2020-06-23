import rosbag
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', '-i', help='input file path', required=True)
    parser.add_argument('--output', '-o', help='output file name', required=True)
    parser.add_argument('--angle', help='clipping angle deg (default = 180)', default=180)
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print("File not exists : %s" % (args.input))
        exit(1)

    if args.input.split(".") == 1 or args.input.split(".")[-1] != 'bag':
        print("File should be rosbag file!")
        exit(1)

    for topic, msg, t in rosbag.Bag(args.input).read_messages():
        print(msg)        

    # with rosbag.Bag('output.bag', 'w') as outbag:
    #     for topic, msg, t in rosbag.Bag(args.input).read_messages():