# RPA for Amazon Checkout Process

During the early days of COVID-19, it was almost impossible to make an online delivery from Whole Foods. Ironically, it was precisely during this time that we had to avoid physically going to grocery stores as much as possible. I didn't want to refresh the page manually every few seconds, so I created a bot that performs this task automatically on my behalf. First I used RPA to sign in to Amazon and get to the checkout page. Then I applied computer vision on the webpage to detect whether a delivery window was available. I also used an SMS API to notify me when to complete the order. Finally, I used Airflow to schedule to run this process every 5 minutes. 

Main libraries used: <br>
- RPA: rpa (https://github.com/tebelorg/RPA-Python) `pip install rpa`
- Computer vision: OpenCV (https://opencv.org/) `pip install opencv-python`
- API: Twilio (https://www.twilio.com/docs/usage/api) `pip install twilio`
- Workflow scheduling: Airflow (https://airflow.apache.org/) `pip install airflow`

For more information on the project, check out http://www.kizzen.io/rpa (or the notebook in this repo: Groceries_Covid.ipynb).

My data science portfolio site: https://kizzen.github.io/
