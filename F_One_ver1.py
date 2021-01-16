# USAGE
# python F_ONE.py

# import necessary packages
from multiprocessing import Manager
from multiprocessing import Process
from imutils.video import VideoStream
from thuvien.objcenter import ObjCenter
# from thuvien.SpeechToAction import SpeechToAction
from thuvien.SpeechToAction import SpeechToAction
# import pantilthat as pth
import argparse
import signal
import time
import datetime
import sys
import cv2
from thuvien.PCA9685 import PCA9685
from thuvien.Common import Common
from thuvien.DetectObject import *
import imutils
from snowboy1 import snowboydecoder
import os
from thuvien.Utils import *
import board
import RPi.GPIO as GPIO
# define the range for the motors
# servoRange = (-90, 90)
servoRange = (0, 180)
pwm = PCA9685()
pwm.setPWMFreq(50)

max_PAN      = 140
max_TILT     = 120
min_PAN      = 50
min_TILT     = 50

max_rate_TILT = 3
max_rate_PAN  = 3

step_PAN     = 1
step_TILT    = 1
default_PAN_Angel  =90
default_TILT_Angel = 70
global finished_servor_process
finished_servor_process = True


interrupted = False
path =os.path.dirname(os.path.realpath(__file__))
model_giong_noi = path+"/F_One.pmdl"

# function to handle keyboard interrupt
def signal_handler(sig, frame):
	# print a status message
	print("[INFO] You pressed `ctrl + c`! Exiting...")
	global interrupted
	interrupted = True
	# disable the servos
	# shut down cleanly
	pwm.exit_PCA9685()
	GPIO.cleanup()
	# exit
	sys.exit()


def interrupt_callback():
	global interrupted
	return interrupted


def thucthi_hanhdong_theo_giongnoi(fname,  *therest ):
	commands = list(therest)
	# print("command 1 = "+ str(commands[0].value)  )
	# dk_canhtay_giongnoi  = commands[0].value

	list_commands = {  "dk_canhtay_giongnoi": commands[0].value,
                            "dk_nhan_dien_hinhanh": commands[1].value,
							"tracking_object_status": commands[2].value }
	speech_to_action = SpeechToAction(fname)
	list_commands = speech_to_action.assistant(list_commands)    
	# os.remove(fname)
	commands[0].value =  list_commands['dk_canhtay_giongnoi']
	commands[1].value =  list_commands['dk_nhan_dien_hinhanh']
	commands[2].value =  list_commands['tracking_object_status']
	print( list_commands )

	# dừng 2s để chụp hình
	if commands[1].value == 1:
		time.sleep(2)
	# nếu "dk_nhan_dien_hinhanh": commands[1].value == 2 thì bắt đầu nhận diện và thông báo
	if commands[1].value == 2 :
		if not os.path.exists("need_to_detect.jpg"):
			print(" Không tim thấy need_to_detect.jpg ")
			speech_to_action.speak("Không tìm thấy hình ảnh")
			commands[1].value = 0
			return;
		else:
			object_dict = detect_object("need_to_detect.jpg")
			if not object_dict:
				print ('empty dict')
				speech_to_action.speak("Không phát hiện bất thường")
			else:
				text = "Phát hiện "
				for key in object_dict:
					text = text + " " + str(object_dict[key]) +" " + str(key)
				print (text)	
				speech_to_action.speak(text)
				family_person_dict = detect_family_person( "need_to_detect.jpg" )
				if  family_person_dict:
					text2 = "Có vẻ là "
					i = 0 
					for key in family_person_dict:
						if i == 0:								
							text2 = text2 + " " + str(key) 
						else:
							text2 = text2 + " và  " + str(key) 	
					print (text2)
					speech_to_action.speak(text2)	
				

		commands[1].value = 0
		os.remove("need_to_detect.jpg") 

	speech_to_action.play_audio_file()





def obj_center(args, objX, objY, centerX, centerY, found_Object, not_Found_Rect_time,dk_nhan_dien_hinhanh):
	# signal trap to handle keyboard interrupt
	signal.signal(signal.SIGINT, signal_handler)

	# start the video stream and wait for the camera to warm up
	vs = VideoStream(src=0).start()
	time.sleep(2.0)

	# initialize the object center finder
	# obj = ObjCenter(args["cascade"])
	obj = ObjCenter("haarcascade_frontalface_default.xml")
	save_img_every_2s = time.time()

	# loop indefinitely
	while True:
		# grab the frame from the threaded video stream and flip it
		# vertically (since our camera was upside down)
		frame = vs.read()
		frame = imutils.resize(frame, width=500)
		# frame = cv2.flip(frame, 1)

		# calculate the center of the frame as this is where we will
		# try to keep the object
		(H, W) = frame.shape[:2]
		
		centerX.value = W // 2
		centerY.value = H // 2

		# 480 x640   - 375x500
		# print("H= "+ str(H) +" W="+str(W))
		# find the object's location
		objectLoc = obj.update(frame, (centerX.value, centerY.value))
		((objX.value, objY.value), rect) = objectLoc
				
		if rect is not None:
			# nếu nhận diện khung mặt thì un-comment
			((x, y), radius) = cv2.minEnclosingCircle(rect)
			# nếu nhận diện theo mau sac  thì un-comment
			cv2.circle(frame, (int(x), int(y)), int(radius),
					(0, 255, 255), 2)
			cv2.circle(frame, (int(objX.value), int(objY.value)), 5, (0, 0, 255), -1)
			text = "objX = " + str(objX.value) +" objY= "+ str(objY.value)
			color = (0, 0, 0)
			cv2.putText(frame,text , (20,20) , cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
			found_Object.value = 1	
			not_Found_Rect_time.value = time.time()
			# print(" H= "+ str(H)+" w = " + str(W ))	
		else:
			found_Object.value = 0
			


		# nếu dk_nhan_dien_hinhanh = 1 thì lưu hình ảnh need_to_detect_image
		if dk_nhan_dien_hinhanh.value ==1:
			
			cv2.imwrite("need_to_detect.jpg", frame)
			dk_nhan_dien_hinhanh.value = 2
		
		# lưu hình ảnh mỗi 2s  - tạm chưa cho hoạt đọng
		# if time.time() - save_img_every_2s > 4 :
		# 	value = datetime.datetime.fromtimestamp(time.time())
		# 	my_date = f"{value:%Y-%m-%d %H:%M:%S}"
		# 	color = (0, 255, 255)
		# 	cv2.putText(frame ,my_date , (20,20) , cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1, cv2.LINE_AA)
		# 	cv2.imwrite("/var/www/lab_app/static/streaming_img.jpg", frame)
		# 	save_img_every_2s = time.time()

		# display the frame to the screen
		cv2.imshow("Pan-Tilt Face Tracking", frame)
		cv2.waitKey(1)

#position servos 
def positionServo (servo, angle, slow_move_current_angle=0):
	a = slow_move_current_angle
	if not slow_move_current_angle == 0:
		while not angle == a:
			if angle > a:
				a = a + 1
			else:
				a = a -1
			pwm.setRotationAngle(servo, a)
			time.sleep(0.05) 

	
	else:
		# os.system("python angleServoCtrl.py " + str(servo) + " " + str(angle))
		pwm.setRotationAngle(servo, angle) 
		# print("[INFO] Positioning servo at GPIO {0} to {1} degrees\n".format(servo, angle))




def set_servos(objX, objY, panAngle, tiltAngle, dk_canhtay_giongnoi, 
				found_Object, not_Found_Rect_time, tracking_object_status):
	
	# signal trap to handle keyboard interrupt
	signal.signal(signal.SIGINT, signal_handler)
	# print( " pan.value = "+ str(pan.value)+" tlt.value = " + str(tlt.value ) )
	
	# loop indefinitely
	while True:
		

		if not  dk_canhtay_giongnoi.value == 0:			
			# xoay cánh tay  0= không làm gì  1= trên 2= dưới 3= trái 4 = phải
			print("Xoay cánh tai theo lệnh "+ str(dk_canhtay_giongnoi.value ))
			if dk_canhtay_giongnoi.value  == 1:
				positionServo (0, 30,tiltAngle.value)
				tiltAngle.value = 30
			elif dk_canhtay_giongnoi.value  == 2:
				positionServo (0, 120,tiltAngle.value)
				tiltAngle.value =120
			elif dk_canhtay_giongnoi.value  == 3:
				positionServo (1, 40,panAngle.value)
				panAngle.value = 40
			elif dk_canhtay_giongnoi.value  == 4:
				positionServo (1, 140, panAngle.value)
				panAngle.value = 140

			dk_canhtay_giongnoi.value  = 0
			time.sleep(2) #dung lai 3s
			# reset lại thời gian, 15s sau mới quay về vị trí mặc định 
			not_Found_Rect_time.value = time.time()
		
		# Nếu tìm thấy vật thể nên not_Found_Object ==1
		elif (found_Object.value == 1):

			if (objX.value < 180):
				panAngle.value += 3
				if panAngle.value > 140:
					panAngle.value = 140
				positionServo (1, panAngle.value) #PAN

			if (objX.value > 350):
				panAngle.value -= 3
				if panAngle.value < 40:
					panAngle.value = 40
				positionServo (1, panAngle.value)

			if (objY.value > 300):
				tiltAngle.value += 3
				if tiltAngle.value > 120:
					tiltAngle.value = 120
				positionServo (0, tiltAngle.value) #TILT

			if (objY.value < 150):
				tiltAngle.value -= 3
				if tiltAngle.value < 40:
					tiltAngle.value = 40
				positionServo (0, tiltAngle.value)

			time.sleep(0.05)
		# 	print ("[INFO] Object Center coordinates at \
		# X0 = {0} and Y0 =  {1}  Pan={2} and tilt = {3}".format(objX.value, objY.value,panAngle.value, tiltAngle.value))
			

		else:
			# Nếu không tìm thấy đối tượng hơn 15s  cam sẽ quay về vị trí cũ
			if time.time() - not_Found_Rect_time.value >= 15:				
				positionServo (1,default_PAN_Angel , panAngle.value) #PAN
				positionServo (0, default_TILT_Angel, tiltAngle.value) #TILT
				tiltAngle.value = default_TILT_Angel
				panAngle.value = default_PAN_Angel
				not_Found_Rect_time.value = time.time()
				print("Back to default position")
				if tracking_object_status.value == 1:
					text_to_speak("Không tìm thấy đối tượng cần theo dõi")


def dieu_khien_theo_giong_noi( dk_canhtay_giongnoi ,dk_nhan_dien_hinhanh, tracking_object_status ):
	model = path +"/F_One.pmdl"
	models = [model, path +"/F_One2.pmdl"]
	# capture SIGINT signal, e.g., Ctrl+C
	signal.signal(signal.SIGINT, signal_handler)
	sensitivity = [0.5]*len(models)
	# detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5,audio_gain=3)
	detector = snowboydecoder.HotwordDetector(models, sensitivity=sensitivity,audio_gain=3)
	print('Listening... Press Ctrl+C to exit')

	recorder_callback = lambda fname,  *therest: thucthi_hanhdong_theo_giongnoi( fname , dk_canhtay_giongnoi ,dk_nhan_dien_hinhanh,
													 tracking_object_status )


	detectedCallbacks = [lambda: detectedCallback(),
             lambda: detectedCallback()]												 
	# main loop
	fname = None
	detector.start(detected_callback=detectedCallbacks,
					sleep_time=0.03,
					audio_recorder_callback=recorder_callback,
					silent_count_threshold=15,
					recording_timeout=150
			)


	detector.terminate()



def detectedCallback():
	snowboydecoder.play_audio_file(snowboydecoder.DETECT_DING)
	print('recording audio...', end='', flush=True)

# check to see if this is the main body of execution
if __name__ == "__main__":
	# construct the argument parser and parse the arguments
	ap = argparse.ArgumentParser()
	# ap.add_argument("-c", "--cascade", type=str, required=True,
		# help="path to input Haar cascade for face detection")
	args = vars(ap.parse_args())

	# khai báo biến toàn cục
	# g.initialize() 


	# start a manager for managing process-safe variables
	with Manager() as manager:
		# enable the servos
		pwm.setRotationAngle(1, default_PAN_Angel) #PAN    
		pwm.setRotationAngle(0, default_TILT_Angel) #TILT
		found_Object = manager.Value("i", 0)
		not_Found_Rect_time = manager.Value("f", time.time())
		# set integer values for the object center (x, y)-coordinates
		centerX = manager.Value("i", 100)
		centerY = manager.Value("i", 50)

		# set integer values for the object's (x, y)-coordinates
		objX = manager.Value("i", 50)
		objY = manager.Value("i", 0)

		# pan and tilt values will be managed by independed PIDs
		pan = manager.Value("i", default_PAN_Angel)
		tlt = manager.Value("i", default_TILT_Angel)

		# biến lưu trạng thái đang tracking object, nếu = 1 là đang tracking , bằng 2 là mất tính hiệu và phát thông báo
		tracking_object_notification = manager.Value("i", 0)	
		# 0= tắt, 1= bật
		tracking_object_status = manager.Value("i", 0)
		# các biến điều khiển thiết bị
		# xoay cánh tay  0= không làm gì  1= trên 2= dưới 3= trái 4 = phải
		dk_canhtay_giongnoi = manager.Value("i", 0)
		dk_led_gn = manager.Value("i", 1)
		# 0 - ko làm gì cả , 1 bắt đầu chụp hình lưu lại với tên need_to_detect.jpg, 2 bắt đầu nhận dạng , speak(), xóa hình ảnh 
		dk_nhan_dien_hinhanh = manager.Value("i", 0)
		# we have 4 independent processes
		# 1. objectCenter  - finds/localizes the object
		# 2. panning       - PID control loop determines panning angle
		# 3. tilting       - PID control loop determines tilting angle
		# 4. setServos     - drives the servos to proper angles based
		#                    on PID feedback to keep object in center
		processObjectCenter = Process(target=obj_center,
			args=(args, objX, objY, centerX, centerY, found_Object, not_Found_Rect_time,dk_nhan_dien_hinhanh))
		processSetServos = Process(target=set_servos, args=(objX, objY, pan, tlt,dk_canhtay_giongnoi,
		 found_Object, not_Found_Rect_time,tracking_object_status))
		processSpeechToAction = Process(target=dieu_khien_theo_giong_noi,
			args=(dk_canhtay_giongnoi, dk_nhan_dien_hinhanh, tracking_object_status))
		# start all 4 processes
		processObjectCenter.start()
		processSetServos.start()
		processSpeechToAction.start()
		# join all 4 processes
		processObjectCenter.join()
		processSetServos.join()
		processSpeechToAction.join()
		# disable the servos
		# shut down cleanly
		pwm.exit_PCA9685()