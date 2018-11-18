# -*- coding: utf8 -*-
"""
Send sms to connected ISP to upgrade data limit
This codes sends an sms automatically via the mr6400 router once the connection is lost
Author: Gijs Entius <g.m.entius@gmail.com>
License: see LICENSE
"""
from tplink_sms import SMSSender
import threading
from datetime import datetime
import os
import logging
import socket
import requests
try:
    import httplib
except:
    import http.client as httplib

SEND_SMS = False  # Used for checking if a sms is sent to revive the internet
logging.basicConfig(level=logging.INFO)  # INFO is standard: change to see more of the logging
CHECK_DELAY = 15  # standard time to wait before running another round of checking


def send_extra_message():
    """
    Sends message
    Config this method to send an message automatically to your isp with the supported message
    """
    global SEND_SMS
    SEND_SMS = True
    sms_sender.send_sms('1GB EXTRA', '1280')


def send_log_message(message):
    """ 
    Sends log message
    Sends log message to default number @see SMSSender
    """
    sms_sender.send_sms(message)


def data_limit_reached():
    """ 
    Checks if internet connection is up
    This method should be adapted to purpose of the program
    In this case the purpose is checking if the data limit is reached
    """
    hostname = 'www.google.com'
    conn = httplib.HTTPConnection(hostname, timeout=3)
    try:
        conn.request("GET", "/")
        response = str(conn.getresponse().read())
        if hostname in response:
            logging.debug(hostname + ' was found at ' + str(datetime.now()))
            return False
        else:
            conn.close()
            logging.debug(hostname + ' was NOT found at ' + str(datetime.now()))
            return True
    except Exception as e:
        logging.error("testing connectivity: " + str(e))
    return True


def internet_upgrade_loop():
    """ 
    Loop for sending sms on connection loss
    This function checks every CHECK_DELAY seconds if the internet connection is lost.
    If the internet connection is lost the program sends an sms defined in send_extra_message
    """
    global SEND_SMS, CHECK_DELAY
    threading.Timer(CHECK_DELAY, internet_upgrade_loop).start()
    if data_limit_reached():
        if SEND_SMS:
            send_log_message(message='Upgrade sms sent: connection still down ' + str(datetime.now()))
            logging.warning('Upgrade sms sent: connection still down ' + str(datetime.now()))
        else:
            logging.info('Data limit reached: ' + str(datetime.now()))
            send_extra_message()
            logging.info('SMS sent to ISP: ' + str(datetime.now()))
    else:
        logging.info('internet connected: ' + str(datetime.now()))
        SEND_SMS = False  # reset sms send loop
    

if __name__ == '__main__':
    sms_sender = SMSSender('sms_config.ini')
    internet_upgrade_loop()