from celery import shared_task
from time import sleep
from django.conf import settings
from django.core.mail import send_mail
# from docx2pdf import convert
# from django.core.files.storage import FileSystemStorage
import os



@shared_task
def send_mail_task(list_of_mail):
    # list_of_mail = ['vatsalvohera70@gmail.com']
    # 
    # 
    for item in list_of_mail:
        send_mail('CELERY WORKED YEAH', "CELERY IS COOL" ,
                settings.EMAIL_HOST_USER,   
                [item],
                fail_silently = False
                )
        print("MAIL FROM CELERY")
    return None