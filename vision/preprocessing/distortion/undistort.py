# Original tutorial: https://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_calib3d/py_calibration/py_calibration.html#calibration

import numpy as np
import cv2
import glob
from copy import copy

import cPickle
filename = "../../vision/calibrations/undistort.txt"

# Set the required dimension of all sample checkboard images
dim = (9,6)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((dim[0]*dim[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:dim[0], 0:dim[1]].T.reshape(-1,2)

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('samples/pitch1/*.png')

for fname in images:

    img = cv2.imread(fname)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, dim, None)

    # If found, add object points, image points (after refining them)
    if ret == True:

        objpoints.append(objp)

        corners2 = copy(corners)
        _ = cv2.cornerSubPix(gray,corners2,(11,11),(-1,-1),criteria)
        imgpoints.append(corners2)

        # Draw and display the corners
        # Comment this out to skip showing sample images!
        _ = cv2.drawChessboardCorners(img, dim, corners2, ret)
        cv2.imshow('img',img)
        cv2.waitKey(1000)

cv2.destroyAllWindows()

# Get the calibration data
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)

capture = cv2.VideoCapture(0)

c = True
while c != 27:
    status, frame = capture.read()
    h,  w = frame.shape[:2]    
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),0,(w,h))

    #These are the actual values needed to undistort:
    dst = cv2.undistort(frame, mtx, dist, None, newcameramtx)

    # crop the image
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]

    cv2.imshow('Original', frame)
    cv2.imshow('Undistorted',dst)

    c = cv2.waitKey(2) & 0xFF

pitch1 = {'new_camera_matrix' : newcameramtx,
        'roi' : roi,
        'camera_matrix' : mtx,
        'dist' : dist}

pitch0 = {'new_camera_matrix' : newcameramtx,
        'roi' : roi,
        'camera_matrix' : mtx,
        'dist' : dist}

data = {0 : pitch0, 1: pitch1}

with open(filename,'wb') as fp:
    cPickle.dump(data,fp)
