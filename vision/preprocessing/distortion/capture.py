# Quick script to help capture sample images.
# It will take a snapshot at regular intervals, save it
# and print a confirmation. You can add a name_offset to continue where
# you left off.
# Press Esc to end it.

import cv2, time

capture = cv2.VideoCapture(0)

interval = 20

start = time.time()
elapsed = 1
name_offset = 0

c = True
while c != 27:
	status, frame = capture.read()
	cv2.imshow('img',frame)
	c = cv2.waitKey(2) & 0xFF

	current = time.time()
	if current-start > elapsed*interval:
		cv2.imwrite('%s_9x6.png' % str(elapsed + name_offset), frame)
    	print "!!!!!!!11!!11   " + str(elapsed + name_offset)
		elapsed += 1


end = time.time()
print end-start
