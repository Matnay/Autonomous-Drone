import rospy
import time
from mavros_msgs.msg import State,PositionTarget
from mavros_msgs.srv import CommandBool, SetMode
from geometry_msgs.msg import Pose, PoseStamped, Point, Quaternion
import math
import numpy
from geometry_msgs.msg import Twist, TwistStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Header, String , Int32,Int8
from threading import Thread
from rospy.numpy_msg import numpy_msg
import pyautogui

def start():
	rate=rospy.Rate(10)
	for i in range (0,100):
		takeoff()
	while not rospy.is_shutdown():
		pos=set_position()
	    #pos.header.frame_id = 'base_link'
	    #pos.header.stamp = rospy.Time.now()
		vel_pub.publish(pos)
		rate.sleep()

def takeoff():
	local_pos_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped, queue_size=10)
	result = arming_srv(value=True)
	#print result
	result = mode_srv(custom_mode="OFFBOARD")
	#print result
	pose = PoseStamped()
	pose.header.stamp = rospy.Time.now()
	pose.pose.position.x = 0
	pose.pose.position.y = 0
	pose.pose.position.z = 4
	local_pos_pub.publish(pose)
	rate.sleep()

def set_position():
	xc,yc = pyautogui.position()
	pos=TwistStamped()
	pos.header = Header()
	#print("xc is " + str(xc))
	if(xc<680 and yc<380):
		pos.twist.linear.z=0.0
		pos.twist.linear.x=1
		pos.twist.linear.y=1
		print("forward_left")
	elif(xc<680 and yc>380):
		pos.twist.linear.z=0.0
		pos.twist.linear.x=1
		pos.twist.linear.y=-1
		print("forward_right")

	elif(xc>680 and yc<380):
		pos.twist.linear.z=0.0
		pos.twist.linear.x=-1
		pos.twist.linear.y=-1
		print("backward_left")

	elif(xc>680 and yc>380):
		pos.twist.linear.z=0.0
		pos.twist.linear.x=-1
		pos.twist.linear.y=1
		print("backward_right")

	else: 
		pos.twist.linear.z=0
		pos.twist.linear.x=0
		pos.twist.linear.y=0
		print("entered default")
	return pos

if __name__ == '__main__':
	rospy.init_node('gaze_control', anonymous=True)
	rate=rospy.Rate(10)
	vel_pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped,queue_size=10)
	arming_srv = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
	mode_srv = rospy.ServiceProxy("/mavros/set_mode", SetMode)
	start()
