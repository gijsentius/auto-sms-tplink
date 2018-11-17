# -*- coding: utf8 -*-
"""
Send sms to telecom company to upgrade data limit
This codes sends an sms automatically via the mr6400 router once the connection is lost
Author: Gijs Entius <g.m.entius@gmail.com>
License: see LICENSE
"""
from tplink_sms import SMSSender
import threading
try:
    import httplib
except:
    import http.client as httplib

SEND_SMS = False  # used for checking if a sms is sent to revive the internet


def send_extra_message():
    """
    Sends message
    Config this method to send an message automatically to your isp with the supported message
    """
    sms_sender.send_sms('1GB EXTRA', '1280')


def send_log_message(message):
    """ 
    Sends log message
    Sends log message to default number @see SMSSender
    """
    sms_sender.send_sms(message)


def internet_connection_up():
    """ 
    Checks if internet connection is up
    """
    conn = httplib.HTTPConnection("www.google.com", timeout=3)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False


def internet_upgrade_loop():
    """ 
    Loop for sending sms on connection loss
    This function checks every 15 seconds if the internet connection is lost.
    If the internet connection is lost the program sends an sms defined in send_extra_message
    """
    threading.Timer(15, internet_upgrade_loop).start()
    if not internet_connection_up():
        if SEND_SMS:
            send_log_message(message='Data limit upgrade sms sent, but it is not working ' + datetime.now())  # using default phone number
            print('Data limit upgrade sms sent, but it is not working ' + datetime.now())
        else:
            send_extra_message()
    else:
        print('internet connected:' + datetime.now())
        SEND_SMS = False  # reset sms send loop
    


if __name__ == '__main__':
    sms_sender = SMSSender('sms_config.ini')
    internet_upgrade_loop()

    