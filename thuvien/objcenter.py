# import necessary packages
import imutils
import cv2

class ObjCenter:
	def __init__(self, haarPath):
		# load OpenCV's Haar cascade face detector
		self.detector = cv2.CascadeClassifier(haarPath)
		# define the lower and upper boundaries of the object
		# to be tracked in the HSV color space
		self.colorLower = (16, 100, 100)   #(24, 100, 100)
		self.colorUpper = (36, 255, 255)   #(44, 255, 255)

	def update(self, frame, frameCenter):
		# convert the frame to grayscale
		# frame = imutils.resize(frame, width=500)
		# frame = imutils.rotate(frame, angle=180)
		hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
		# construct a mask for the object color, then perform
		# a series of dilations and erosions to remove any small
		# blobs left in the mask
		mask = cv2.inRange(hsv, self.colorLower, self.colorUpper)
		mask = cv2.erode(mask, None, iterations=2)
		mask = cv2.dilate(mask, None, iterations=2)

		# find contours in the mask and initialize the current
		# (x, y) center of the object
		cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
			cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv4() else cnts[1]
		center = None
		
		# only proceed if at least one contour was found
		if len(cnts) > 0:
			# find the largest contour in the mask, then use
			# it to compute the minimum enclosing circle and
			# centroid
			c = max(cnts, key=cv2.contourArea)
			((x, y), radius) = cv2.minEnclosingCircle(c)
			M = cv2.moments(c)
			center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

			# only proceed if the radius meets a minimum size
			if radius > 20:
				# draw the circle and centroid on the frame,
				# then update the list of tracked points
				# cv2.circle(frame, (int(x), int(y)), int(radius),
				# 	(0, 255, 255), 2)
				# cv2.circle(frame, center, 5, (0, 0, 255), -1)
				
				return ((int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])), c) 
				# return ((int(x), int(y)), c) 
			# cv2.imshow("MAsk", mask)
		# otherwise no faces were found, so return the center of the
		# frame
		return (frameCenter, None)

	# nếu muốn dùng face detect thì sửa lại thành update()
	def update_old_for_face_detect(self, frame, frameCenter):
		# convert the frame to grayscale
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

		# detect all faces in the input frame
		rects = self.detector.detectMultiScale(gray, scaleFactor=1.05,
			minNeighbors=9, minSize=(30, 30),
			flags=cv2.CASCADE_SCALE_IMAGE)

		# check to see if a face was found
		if len(rects) > 0:
			# extract the bounding box coordinates of the face and
			# use the coordinates to determine the center of the
			# face
			(x, y, w, h) = rects[0]
			faceX = int(x + (w / 2.0))
			faceY = int(y + (h / 2.0))

			# return the center (x, y)-coordinates of the face
			return ((faceX, faceY), rects[0])

		# otherwise no faces were found, so return the center of the
		# frame
		return (frameCenter, None)