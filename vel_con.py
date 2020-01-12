#!/usr/bin/env python

import rospy
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode
from geometry_msgs.msg import Pose, PoseStamped, Point, Quaternion
import math
import numpy
from geometry_msgs.msg import Twist
from std_msgs.msg import Header
from threading import Thread
x=1
print x

def start1():
    global x
    rate = rospy.Rate(20) # Hz
    if x==1:
      print "Arming"
      result = arming_srv(value=True)
      print result
      print "Setting Offboard Mode"
      result = mode_srv(custom_mode="OFFBOARD")
      print result
      x=0
   
    print "position_set"
    
    
    while not rospy.is_shutdown():
        print "Setting Offboard Mode"
        result = mode_srv(custom_mode="OFFBOARD")
        print result
        x=0
        pos=set_p()
        pos.header.stamp = rospy.Time.now()
        vel_pub.publish(pos)
        
        try:
           rate.sleep()
        except rospy.ROSInterruptException:
           pass
    
def state_cb(msg):
    print msg
def set_p():
    pos=PoseStamped()
    pos.header = Header()
    #enter position for the drone
    pos.pose.position.x=0
    pos.pose.position.y=0
    pos.pose.position.z=5.0
    return pos
    
if __name__ == '__main__':
    rospy.init_node('subnode', anonymous=True)
    vel_pub = rospy.Publisher('/mavros/setpoint_position/local', PoseStamped,queue_size=1)
    arming_srv = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
    mode_srv = rospy.ServiceProxy("/mavros/set_mode", SetMode)
    start1()
    pos_thread = Thread(target=start1, args=())
    pos_thread.daemon = True
    pos_thread.start()
    state_sub = rospy.Subscriber('/mavros/state', State, callback=state_cb)
    
   
    

    


    


