import rpa as r
import numpy as np
import cv2
from PIL import Image
import pytesseract
from twilio.rest import Client

# open browser
r.init(True) 
# go to amazon sign in page
r.url('https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26action%3Dsign-out%26path%3D%252Fgp%252Fyourstore%252Fhome%26ref_%3Dnav_youraccount_signout%26signIn%3D1%26useRedirectOnSuccess%3D1')
# sign into amazon account
r.type('text','******[enter]') # enter amazon username here
r.type('text','*******[enter]') # enter password here
# click to go to delivery window page
r.click('Cart')
r.click('Checkout Whole Foods Market Cart')
r.click('continue')
r.click('continue')
r.wait(20)
# save screenshot file
r.snap('page','results.png')

# use open to extract delivery availability msg
filename = 'results.png'
img = cv2.imread(filename)
imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)# convert to gray
filename_gray = filename + '_box.jpg'
cv2.imwrite(filename_gray, imgray)
r.close()

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

# draw contour for 6
cv2.drawContours(imgray,box_lst,6,(0,255,0),2)
# cv2.imshow('Rectangles', imgray) 
# cv2.waitKey(0)
cv2.imwrite(filename_gray, imgray)

img = cv2.imread(filename_gray)
coordinates = box_lst[6]
x1 = coordinates[2][0]
x2 = coordinates[0][0]
y1 = coordinates[2][1]
y2 = coordinates[0][1]

crop_img = img[y1:y2, x1:x2]
cv2.imwrite(filename_gray, crop_img)

# use OCR to convert image to string
msg = pytesseract.image_to_string(Image.open(filename_gray))
print(msg)
# msg = No dehvery wmdows avauable, New wmdows are re‘eased throughout the day.

# try resizing image to remove typos in OCR
src = cv2.imread(filename_gray, cv2.IMREAD_UNCHANGED)
_,thresh = cv2.threshold(src, 180,255, cv2.THRESH_BINARY_INV)
cv2.imwrite(filename_gray,thresh)
msg = pytesseract.image_to_string(Image.open(filename_gray))
print(msg)
# No delivery windows available. New windows are released throughout the day.

# do not share this - need to add number on Twilio to receive text message
# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
if msg == 'No delivery windows available. New windows are released throughout the day.':
	account_sid = '************'
	auth_token = '************'
	client = Client(account_sid, auth_token)
	message = client.messages.create(
	                              body='notification to order from amazon',
	                              from_='************',
	                              to='************')
else:
	pass
