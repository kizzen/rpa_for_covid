import numpy as np
import cv2

# use open to extract delivery availability msg
filename = 'results.png'
img = cv2.imread(filename)
imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)# convert to gray
filename_gray = filename + '_box.jpg'
cv2.imwrite(filename_gray, imgray)

_,thresh = cv2.threshold(imgray, 180,255, cv2.THRESH_BINARY_INV)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)) #rectangle shape
dilated = cv2.dilate(thresh, kernel,iterations=2)

contours, hierarchy = cv2.findContours(dilated.copy(),cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

box_lst = []
for cnt in contours:
	area = cv2.contourArea(cnt)
	rect=cv2.minAreaRect(cnt)

	box=cv2.boxPoints(rect)
	box=np.int0(box)
	box_lst.append(box)

box_lst = sorted(box_lst, key=cv2.contourArea, reverse=True)
print(box_lst)
print(len(box_lst))

# through iteration find the box number 6
for i in range(len(box_lst)):
	cv2.drawContours(imgray,box_lst,i,(0,255,0),10)
	cv2.imshow('Rectangles', imgray) 
	cv2.waitKey(0)

# draw contour for 6
cv2.drawContours(imgray,box_lst,6,(0,255,0),10)
cv2.imshow('Rectangles', imgray) 
cv2.waitKey(0)