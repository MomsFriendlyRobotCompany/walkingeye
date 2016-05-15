#!/usr/bin/env python
#
# by Kevin J. Walchko 26 Aug 2014
#
# Log:
# 12 Oct 14 Broke out into its own file
#

import time
import datetime as dt
import multiprocessing as mp
import logging
# import yaml
#import socket
import IMU.MotorDriver as md
import RPi.GPIO as GPIO # IR

from zmqclass import *

# def test():
# 	import time
# 	mmd = md.MotorDriver(17,18,22,23)
# 	
# 	go  = {'dir': MotorDriver.FORWARD, 'duty': 50}
# 	rev = {'dir': MotorDriver.REVERSE, 'duty': 100}
# 	stp = {'dir': MotorDriver.REVERSE, 'duty': 0}
# 	
# 	mmd.setMotors(go,go,go,go)
# 	time.sleep(10)
# 	mmd.setMotors(rev,rev,rev,rev)
# 	time.sleep(10)
# 	mmd.setMotors(go,stp,go,stp)
# 	time.sleep(10)
# 	mmd.setMotors(stp,rev,stp,rev)
# 	time.sleep(10)
# 	mmd.allStop()

class DigitalIR(object):
	"""
	Read IR sensors on digital inputs

	Pololu sds01a 0-5 cm pwr 3V output max 3V
	Sharp xxx 0-15 cm pwr 5V output max 3V - digital gives 3 inch range
	"""
	def __init__(self, pins):
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		for p in pins: GPIO.setup(p, GPIO.IN)
		self.pins = pins

	def read(self):
		ir = []
		for p in pins: ir.append( GPIO.input(p) )
		return ir

####################################################################
# RobotHardwareServer handles incoming commands streamed from somewhere else.
# All information is in coming.
#
# todo:
# - need to breakout into holonomic and nonholonomic
#
####################################################################
class RobotHardwareServer(mp.Process):
	def __init__(self,host="localhost",port=9000):
		mp.Process.__init__(self)
		self.host = host
		self.port = port
		logging.basicConfig(level=logging.INFO)
		self.logger = logging.getLogger('robot')
# 		self.md = md.MotorDriver(11,12,15,16)
		self.md = None

	def createMotorCmd(dir,duty):
		return {'dir': dir, 'duty': duty}

	def soundCmd(self,cmd):
		self.logger.info( cmd )

	def parseMsg(self, msg):
		if 'quit' in msg:
			self.shutdown()
		elif 'cmd' in msg:
			cmd = msg['cmd']
			if 'm' in cmd:
				self.motorCmd( cmd )
			elif 's' in cmd:
				self.soundCmd( cmd )
	def __del__(self):
		self.md.allStop()
		
	def on_message(self,client, userdata, msg):
		print(msg.topic+' '+str(msg.payload))

	def shutdown(self):
# 		self.pub.close()
# 		exit()
		0

	def test(self):
		dt = 5
		go  = {'dir': md.MotorDriver.FORWARD, 'duty': 10}
		rev = {'dir': md.MotorDriver.REVERSE, 'duty': 10}
		stp = {'dir': md.MotorDriver.REVERSE, 'duty': 10}
	
		self.md.setMotors(go,go,go,go)
		time.sleep(dt)
# 		self.md.setMotors(rev,rev,rev,rev)
# 		time.sleep(dt)
# 		self.md.setMotors(go,stp,go,stp)
# 		time.sleep(dt)
# 		self.md.setMotors(stp,rev,stp,rev)
# 		time.sleep(dt)
# 		self.md.allStop()
		
	def run(self):
		self.logger.info(str(self.name)+'['+str(self.pid)+'] started on'+
			str(self.host) + ':' + str(self.port) +', Daemon: '+str(self.daemon))
		#p = Publisher((self.host,self.port))
		#self.pub = p.accept()
		#self.logger.info('Accepted connection: ')


		self.sub = Sub(['cmds'])

		while True:
			time.sleep(0.05) # 0.5 => 20Hz
			# get info
			msg = self.sub.recv()
# 			if msg:
# 				self.parseMsg( msg )
				
			self.test()
			
			

class NonHolonomic(RobotHardwareServer):
	def __init__(self,host="localhost",port=9000):
		RobotHardwareServer.__init__(self,host,port)
		self.md = md.MotorDriver(11,12)

	def motorCmd(self,cmd):
		self.logger.info(cmd)
		self.md.setMotors(cmd)

class Holonomic(RobotHardwareServer):
	def __init__(self,pinA=11,pinB=12,pinC=15,pinD=16):
		RobotHardwareServer.__init__(self)
		self.md = md.MotorDriver(pinA,pinB,pinC,pinD)

	def motorCmd(self,cmd):
		self.logger.info(cmd)
		self.md.setMotors(cmd)
		



if __name__ == '__main__':
	c = Holonomic()
	c.run()