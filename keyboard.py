import rospy
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, SetMode
from geometry_msgs.msg import Pose, PoseStamped, Point, Quaternion
import math
import numpy as np
from geometry_msgs.msg import Twist, TwistStamped
from nav_msgs.msg import Odometry
from std_msgs.msg import Header, String , Int8
from threading import Thread
import pygame
pygame.init()
screen = pygame.display.set_mode((40, 40))
pygame.display.flip()
clock = pygame.time.Clock()

x=1
ekm1x=0
ekm1y=0
ekm1z=2
take_off=1
hold=0
holdkm1=0
xreal=0
yreal=0
zreal=0
count=0
land=0
hold_refr=[0,0,3]
print x

def start1():
    global x
    
    rate = rospy.Rate(20) # Hz
    pygame.event.pump()
    keys=pygame.key.get_pressed()
    print "start"
    if keys[pygame.K_t]:
       x=1
       print "take_off"
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
        pos=set_p()
        print "Setting Offboard Mode"
        result = mode_srv(custom_mode="OFFBOARD")
        print result
        pos.header.stamp = rospy.Time.now()
        print pos
        vel_pub.publish(pos)
        print "ok"
        try:
           rate.sleep()
           print "sleep"
        except rospy.ROSInterruptException:
           pass
    
def state_cb(msg):
    print msg
def odom_cb(msg1):
    global xreal
    global yreal
    global zreal
    xreal= msg1.pose.position.x
    yreal= msg1.pose.position.y
    zreal= msg1.pose.position.z
    zang=msg1.pose.orientation.z
    
    
    
def set_p():
    global hold
    global holdkm1
    global hold_refr
    hold=0
    pos=TwistStamped()
    pos.twist=Twist()
    pos.header = Header()
    if take_off==1:
       cont=con() 
       pos.twist.linear.x=cont[0]
       pos.twist.linear.y=cont[1]
       pos.twist.linear.z=cont[2]
    else:
       pos.twist.linear.x=0
       pos.twist.linear.y=0
       pos.twist.linear.z=0
       pos.twist.angular.z=0
       pygame.event.pump()
       keys=pygame.key.get_pressed()
    
       if keys[pygame.K_w]:
          pos.twist.linear.x=.8
       elif keys[pygame.K_s]:
          pos.twist.linear.x=-.8
       elif keys[pygame.K_d]:
          pos.twist.linear.y=.8
       elif keys[pygame.K_a]:
          pos.twist.linear.y=-.8
       elif keys[pygame.K_q]:
          pos.twist.linear.z=.8
          print "rise"
       elif keys[pygame.K_e]:
          pos.twist.linear.z=-.8
       elif keys[pygame.K_l]:
          print "Dis-Arming"
          result = arming_srv(value=False)
          print result
          print "Landed"
       elif keys[pygame.K_z]:
          pos.twist.angular.z=.5
          hold=1
          cont=con()
          pos.twist.linear.x=cont[0]
          pos.twist.linear.y=cont[1]
          pos.twist.linear.z=cont[2]
       elif keys[pygame.K_x]:
          pos.twist.angular.z=-.5
          hold=1
          cont=con()
          pos.twist.linear.x=cont[0]
          pos.twist.linear.y=cont[1]
          pos.twist.linear.z=cont[2]
       else:
          hold=1
          if holdkm1==0 and hold==1:
             hold_refr=hold_ref()
       
          cont=con()
          pos.twist.linear.x=cont[0]
          pos.twist.linear.y=cont[1]
          pos.twist.linear.z=cont[2] 
          pos.twist.angular.z=0
    print "hold:"
    print hold_refr
    holdkm1=hold  
    return pos
def con():
    global xreal
    global yreal
    global zreal
    global ekm1x
    global ekm1y
    global ekm1z   
    kp=0.7
    if take_off==1:
       ref=takeoff(ekm1z)
       refx=ref[0]
       refy=ref[1]
       refz=ref[2]
    elif land==1:
       ref=landing()
       refx=ref[0]
       refy=ref[1]
       refz=ref[2]
    if hold==1:
       refx=hold_refr[0]
       refy=hold_refr[1]
       refz=1
    odom_sub  = rospy.Subscriber('/mavros/local_position/pose', PoseStamped, callback=odom_cb)
    errorz=refz-zreal+6
    print errorz
    errorx=refx-xreal
    errory=refy-yreal
    ekm1x=errorx
    ekm1y=errory
    ekm1z=errorz
    if abs(ekm1x)<0.2 and abs(ekm1y)<0.2 and abs(ekm1z)<0.2 and land==1:
       print "Dis-Arming"
       result = arming_srv(value=False)
       print result
       print "Landed"
    else:
       print "x_pos:"
       print xreal
       print "ref_x:"
       print refx
       print "y_pos:"
       print yreal
       print "ref_y:"
       print refy
       print "z_pos:"
       print zreal
       print "ref_z:"
       print refz
    con_com_z=kp*errorz
    con_com_x=kp*errorx
    con_com_y=kp*errory
    out=np.array([con_com_x,con_com_y,con_com_z])
    return out

def hold_ref():
    odom_sub  = rospy.Subscriber('/mavros/local_position/pose', PoseStamped, callback=odom_cb)
    out=np.array([xreal,yreal,zreal])
    return out    
def takeoff(zz):
    global take_off
    if take_off==1:
       refx=0
       refy=0
       refz=6
       if zz<0.1:
          take_off=0
          hold=1
    out=np.array([refx,refy,refz])
    return out
if __name__ == '__main__':
    rospy.init_node('finenode', anonymous=True)
    vel_pub = rospy.Publisher('/mavros/setpoint_velocity/cmd_vel', TwistStamped,queue_size=10)
    arming_srv = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
    mode_srv = rospy.ServiceProxy("/mavros/set_mode", SetMode)
    start1()
    pos_thread = Thread(target=start1, args=())
    pos_thread.daemon = True
    pos_thread.start()
    #state_sub = rospy.Subscriber('/mavros/state', State, callback=state_cb)
