# -*- coding: utf8 -*-
"""
Send SMS via TP-Link TL-MR6400.
This code shows how to send an SMS using the admin GUI of the above router.
Author: Fabio Pani <fabiux@fabiopani.it> & Gijs Entius <g.m.entius@gmail.com>
Github: https://github.com/fabiux/tplink_sms & 
License: see LICENSE
"""
from hashlib import md5
from base64 import b64encode
from datetime import datetime
from time import strftime
import requests
import configparser
import os
import logging

logging.basicConfig(level=logging.INFO)  # INFO is standard: change to see more of the logging


class SMSSender:

    def __init__(self, config_ini_file):
        self.config(config_ini_file)

    def config(self, config_ini_file):
        config = configparser.ConfigParser()
        config.read(config_ini_file)
        self.router_domain = config['DEFAULT']['router_domain']
        self.router_url = 'http://' + self.router_domain + '/'
        self.router_login_path = 'userRpm/LoginRpm.htm?Save=Save'
        self.router_sms_referer = '/userRpm/_lte_SmsNewMessageCfgRpm.htm'
        self.router_sms_action = '/userRpm/lteWebCfg'
        self.router_admin = config['DEFAULT']['router_admin']
        self.router_pwd = config['DEFAULT']['router_pwd']
        self.default_number = config['DEFAULT']['default_number']
    
    def send_sms(self, msg, phone_num=None):
        """
        Send an SMS via TP-Link TL-MR6400.
        :param phone_num: recipient's phone number
        :type phone_num: str
        :param msg: message to send
        :type msg: str
        """

        # phone number allocation
        if phone_num == None:
            phone_num = self.default_number

        # SMS payload
        date_format_linux = '%Y,%-m,%-d,%-H,%-M,%-S'
        date_format_windows = '%Y,%m,%d,%H,%M,%S'
        date_format = date_format_windows if os.name == 'nt' else date_format_linux
        sms = {'module': 'message',
            'action': 3,
            'sendMessage': {
                'to': phone_num,
                'textContent': msg,
                'sendTime': strftime(date_format_windows, datetime.now().timetuple())
            }}

        # authentication
        authstring = self.router_admin + ':' + md5(self.router_pwd.encode('utf-8')).hexdigest()
        authstring = 'Basic ' + b64encode(authstring.encode('utf-8')).decode('utf-8')
        cookie = {'Authorization': authstring, 'Path': '/', 'Domain': self.router_domain}
        s = requests.Session()
        r = s.get(self.router_url + self.router_login_path, cookies=cookie)
        if r.status_code != 200:
            logging.info("status code:" + str(r.status_code))
            exit()
        hashlogin = r.text.split('/')[3]
        sms_form_page = self.router_url + hashlogin + self.router_sms_referer
        sms_action_page = self.router_url + hashlogin + self.router_sms_action

        # send SMS
        s.headers.update({'referer': sms_form_page})
        r = s.post(sms_action_page, json=sms, cookies=cookie)
        if r.status_code != 200:
            logging.info("status code:" + str(r.status_code))

