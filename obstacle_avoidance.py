#!/usr/bin/env python
from std_msgs.msg import Int32
import rospy, cv2, cv_bridge, numpy
from sensor_msgs.msg import Image
import cv2
import numpy as np
from matplotlib import pyplot as plt

class Follower:
	def __init__(self):
		self.bridge = cv_bridge.CvBridge()
		#self.image_sub = rospy.Subscriber('/usb_cam/image_raw',Image, self.image_callback)
		self.image_sub = rospy.Subscriber('/iris/vi_sensor/left/image_raw',Image, self.image_callback)
		self.object_detected=rospy.Publisher('object_detected',Int32,queue_size=10)
	def image_callback(self, msg):
		#image = self.bridge.imgmsg_to_cv2(msg)
		gray = self.bridge.imgmsg_to_cv2(msg)		
		#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)				
		_, gray = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
		gaus = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 91, 12)
		mean_c = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 15, 12)
		height=gray.shape[0]
		width=gray.shape[1]
		count=0
		flag=0
		for i in range(117,368):
			for j in range(221,472):
				if gray[i,j]==0:
					count=count+1
		if count>20000:
			print ("near object detected")
			flag=2
		elif count>10000:
			print ("object detected")
			flag=1				
		#print ("count is %f"%count)
		cv2.imshow("window", gray )
		cv2.waitKey(3)
		self.object_detected.publish(flag)
		

rospy.init_node('follower')
follower = Follower()
rospy.spin()
