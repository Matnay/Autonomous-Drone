#!/usr/bin/env python 
import rospy
import time
from commander import Commander
from std_msgs.msg import Int32 
import rospy
from mavros_msgs.msg import GlobalPositionTarget, State
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from geometry_msgs.msg import PoseStamped, Twist
from sensor_msgs.msg import Imu, NavSatFix, LaserScan
from std_msgs.msg import Float32, String
from pyquaternion import Quaternion
import time
import math

class Commander:
    def __init__(self):
    	global current_pose
        rospy.init_node("commander_node")
        rate = rospy.Rate(40)
	
	#these topics can be remapped to work even on a real drone by publishing to mavros 
        self.position_target_pub = rospy.Publisher('gi/set_pose/position', PoseStamped, queue_size=10)
        self.yaw_target_pub = rospy.Publisher('gi/set_pose/orientation', Float32, queue_size=10)
        self.custom_activity_pub = rospy.Publisher('gi/set_activity/type', String, queue_size=10)
	self.current_pose=rospy.Subscriber('mavros/local_position/pose',PoseStamped,self.pose_callback )
	self.range_obstacle=rospy.Subscriber('scan',LaserScan,self.obj_callback) 
	
    def pose_callback(self,msg):
    	global current_position
    	current_position=msg	
    	return current_position
    	
    def obj_callback(self,msg):
	global obstacle
	range_ahead=msg.ranges[len(msg.ranges)/2]
	range_ahead_2=msg.ranges[len(msg.ranges)/2 - 1]
	range_ahead_3=msg.ranges[len(msg.ranges)/2 + 1]
	range_ahead_4=msg.ranges[len(msg.ranges)/2 + 2]
	print range_ahead
	if range_ahead<4 or range_ahead_2<4 or range_ahead_3<4 or range_ahead_4<4:
		obstacle=2
		print ('near obstacle detected')
	if range_ahead<6 or range_ahead_2<6 or range_ahead_3<6 or range_ahead_4<6:
		obstacle=1
		print ('obstacle detcted')
	if range_ahead>=6 and range_ahead_2>=6 and range_ahead_3>=6:
		obstacle=0
		print ('path clear')	
	return obstacle		

    def move(self, x, y, z, BODY_OFFSET_ENU=True):
        self.position_target_pub.publish(self.set_pose(x, y, z, BODY_OFFSET_ENU))


    def turn(self, yaw_degree):
        self.yaw_target_pub.publish(yaw_degree)

    
    # land at current position
    def land(self):
        self.custom_activity_pub.publish(String("LAND"))


    # hover at current position
    def hover(self):
        self.custom_activity_pub.publish(String("HOVER"))


    # return to home position with defined height
    def return_home(self, height):
        self.position_target_pub.publish(self.set_pose(0, 0, height, False))


    def set_pose(self, x=0, y=0, z=2, BODY_OFFSET_ENU = True):
        pose = PoseStamped()
        pose.header.stamp = rospy.Time.now()

        # ROS uses ENU internally, so we will stick to this convention

        if BODY_OFFSET_ENU:
            pose.header.frame_id = 'base_link'

        else:
            pose.header.frame_id = 'map'

        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = z

        return pose			

if __name__ == "__main__":
    con = Commander()
    time.sleep(1)
    target=PoseStamped()
    #THIS IS WHERE THE TARGET IS SET
	#CHANGE ACCORDING TO WHERE THE DRONE IS BEING TESTED
	#CPS BUILDING INDOORS <2m
    target.pose.position.x= 10
    target.pose.position.y= 0
    target.pose.position.z= 1
    while True:     
	    if current_position.pose.position.x <= target.pose.position.x- 0.2:
	    	print ('moving x')
	    	if obstacle==0:
	    		con.move(2,0,0)
	    		time.sleep(2)
		elif obstacle==1:
			con.move(0,3,0)
			time.sleep(2)
		elif obstacle==2:
			con.move(-1,3,0)
			time.sleep(2)
	    else: 
		con.move(-0.5,0,0)
		time.sleep(2) 
				    		
	    if current_position.pose.position.y <= target.pose.position.y- 0.2:
	   	print ('moving y')
		con.move(0,1,0)
	    	time.sleep(2)
	    	
	    elif current_position.pose.position.y >= target.pose.position.y+ 0.2:
	    	print ('moving y')
	    	con.move(0,-1,0)
	    	time.sleep(2)
	    			
	    if current_position.pose.position.z <= target.pose.position.z+ 0.2:
	    	print ('moving z')	 	    
	       	con.move(0,0,0.5)	
	       	time.sleep(2)
	    else :	
	       	con.move(0,0,-0.5)
	       	time.sleep(2) 
    	    if current_position.pose.position.x<=target.pose.position.x+0.2 and current_position.pose.position.x>=target.pose.position.x-0.2:
		if current_position.pose.position.y<=target.pose.position.y+0.2 and current_position.pose.position.y >= target.pose.position.y-0.2:
			if current_position.pose.position.z<=target.pose.position.z and current_position.pose.position.z >= target.pose.position.z -0.2:
				print("arrived at destination")
				break 	 
