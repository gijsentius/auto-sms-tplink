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
import logging
import sys
try:
    import httplib
except:
    import http.client as httplib

# configs
CHECK_DELAY = 2  # standard time to wait before running another round of checking
SEND_SMS = False  # used for checking if a sms is sent to revive the internet
ALERT = False
FILENAME = "info.log"  # the name of the log file (may include full path)

# logging configuration
logger = logging.getLogger('auto-sms-logger')
logger.propagate = 0  # did not think the propagate setting was important

# create a file handler and stream handler
f_handler = logging.FileHandler(FILENAME)
f_handler.setLevel(logging.DEBUG)
s_handler = logging.StreamHandler()
s_handler.setLevel(logging.INFO)

# assign format to handlers
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
f_handler.setFormatter(formatter)
s_handler.setFormatter(formatter)

logger.addHandler(s_handler)
logger.addHandler(f_handler)


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
            logger.debug(hostname + ' was found')
            return False
        else:
            conn.close()
            logger.debug(hostname + ' was NOT found')
            return True
    except Exception as e:
        logger.error('testing connectivity: ', exc_info=True)
    return True


def internet_upgrade_loop():
    """ 
    Loop for sending sms on connection loss
    This function checks every CHECK_DELAY seconds if the internet connection is lost.
    If the internet connection is lost the program sends an sms defined in send_extra_message
    """
    global SEND_SMS, CHECK_DELAY, ALERT
    threading.Timer(CHECK_DELAY, internet_upgrade_loop).start()
    if data_limit_reached():
        if SEND_SMS and not ALERT:
            send_log_message(message='Upgrade sms sent: connection still down')
            logger.warning('Upgrade sms sent: connection still down')
            ALERT = True
        else:
            logger.info('Data limit reached')
            send_extra_message()
            logger.info('SMS sent to ISP')
    else:
        logger.info('internet connected')
        SEND_SMS = False  # reset sms send loop
        ALERT = False  # reset alert message


if __name__ == '__main__':
    sms_sender = SMSSender('sms_config.ini')
    internet_upgrade_loop()