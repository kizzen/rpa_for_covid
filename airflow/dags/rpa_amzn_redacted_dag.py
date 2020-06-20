from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

import rpa as r
import numpy as np
import cv2
from PIL import Image
import pytesseract
from twilio.rest import Client

def open_browser():
	r.init(True)

def sign_in_page():
	r.url('https://www.amazon.com/ap/signin?_encoding=UTF8&openid.assoc_handle=usflex&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.mode=checkid_setup&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&openid.ns.pape=http%3A%2F%2Fspecs.openid.net%2Fextensions%2Fpape%2F1.0&openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2Fgp%2Fyourstore%2Fhome%3Fie%3DUTF8%26action%3Dsign-out%26path%3D%252Fgp%252Fyourstore%252Fhome%26ref_%3Dnav_youraccount_signout%26signIn%3D1%26useRedirectOnSuccess%3D1')

def username_pw():
	r.type('text','********[enter]')
	r.type('text','********[enter]')

def checkout():
	r.click('Cart')
	r.click('Checkout Whole Foods Market Cart')
	r.click('continue')
	r.click('continue')

def snap():
	r.wait(20)
	r.snap('page','results.png')

def convert_to_greyscale(**context):
	filename = 'results.png'
	img = cv2.imread(filename)
	imgray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)# convert to gray
	context['ti'].xcom_push(key='imgray',value=imgray)
	context['ti'].xcom_push(key='filename',value=filename)
	filename_gray = filename + '_box.jpg'
	context['ti'].xcom_push(key='filename_gray',value=filename_gray)
	# save img
	cv2.imwrite(filename_gray, imgray)
	r.close()

def threshold(**context):
	to_print = context['ti'].xcom_pull('filename')
	print(to_print)
	_,thresh = cv2.threshold(imgray, 180,255, cv2.THRESH_BINARY_INV)
	kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5)) #rectangle shape
	dilated = cv2.dilate(thresh, kernel,iterations=2)

def draw_boxes():
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
	cv2.imwrite(filename_gray, imgray)

def crop():
	img = cv2.imread(filename_gray)
	coordinates = box_lst[6]
	x1 = coordinates[2][0]
	x2 = coordinates[0][0]
	y1 = coordinates[2][1]
	y2 = coordinates[0][1]

	crop_img = img[y1:y2, x1:x2]
	cv2.imwrite(filename_gray, crop_img)

def ocr():
	msg = pytesseract.image_to_string(Image.open(filename_gray))
	print(msg)
	# msg = No dehvery wmdows avauable, New wmdows are re‘eased throughout the day.
	# try resizing image to remove typos in OCR
	src = cv2.imread(filename_gray, cv2.IMREAD_UNCHANGED)
	_,thresh = cv2.threshold(src, 180,255, cv2.THRESH_BINARY_INV)
	# cv2.imshow("thresh", thresh)
	# cv2.waitKey(0)
	cv2.imwrite(filename_gray,thresh)
	msg = pytesseract.image_to_string(Image.open(filename_gray))
	print(msg)

def send_sms():
	if msg == 'No delivery windows available. New windows are released throughout the day.':
		account_sid = '********'
		auth_token = '********'
		client = Client(account_sid, auth_token)
		message = client.messages.create(
		                              body='notification to order from amazon',
		                              from_='********',
		                              to='********')
	else:
		pass

dag = DAG('rpa_amazn', description='rpa_amazn', schedule_interval='0,5,10,15,20,25,30,35,40,45,50,55 * * * *', start_date=datetime(2017, 3, 20), catchup=False)
open_browser = PythonOperator(task_id='open_browser', python_callable=open_browser, provide_context=True,dag=dag)
sign_in_page = PythonOperator(task_id='sign_in_page', python_callable=sign_in_page, dag=dag)
username_pw = PythonOperator(task_id='username_pw', python_callable=username_pw, dag=dag)
checkout = PythonOperator(task_id='checkout', python_callable=checkout, dag=dag)
snap = PythonOperator(task_id='snap', python_callable=snap, dag=dag)
convert_to_greyscale = PythonOperator(task_id='convert_to_greyscale', python_callable=convert_to_greyscale, dag=dag)
threshold = PythonOperator(task_id='threshold', python_callable=threshold, provide_context=True,dag=dag)
draw_boxes = PythonOperator(task_id='draw_boxes', python_callable=draw_boxes, dag=dag)
crop = PythonOperator(task_id='crop', python_callable=crop, dag=dag)
ocr = PythonOperator(task_id='ocr', python_callable=ocr, dag=dag)
send_sms = PythonOperator(task_id='send_sms', python_callable=send_sms, dag=dag)

open_browser >> sign_in_page
sign_in_page >> username_pw
username_pw >> checkout
checkout >> snap
snap >> convert_to_greyscale
convert_to_greyscale >> threshold
threshold >> draw_boxes
draw_boxes >> crop
crop >> ocr
ocr >> send_sms
