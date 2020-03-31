# -*- coding: utf-8 -*-
# @Time    : 2020/3/31 23:40
# @Author  : Edgar Tang
# @Email   : tctco001@gmail.com
# @File    : Synchronizer.py
# @Software: PyCharm

import execjs
import requests
from bs4 import BeautifulSoup
import threading
import time
from functools import wraps

from database import Base, engine, Session, Lesson
from constants import LOGIN_URL, QUERY_URL


def _draw_bar(loading):
    l = ['-', '\\', '/']
    while True:
        for c in l:
            time.sleep(0.2)
            if loading():
                print('\r' + c, end='')
            else:
                return


def add_process_bar(f):
    """
    decorator, add process bar to function f
    :param f: any function that takes time to execute
    :return:
    """

    @wraps(f)
    def _draw_process_bar(*args, **kwargs):
        loading = True
        t = threading.Thread(target=_draw_bar, args=(lambda: loading,))
        t.setDaemon(True)
        t.start()
        f(*args, **kwargs)
        loading = False

    return _draw_process_bar


class Synchronizer:
    def __init__(self):
        """
        username:str: hust pass username
        password:str: hust pass password
        start_time:str: query start time 0000-00-00
        end_time:str: query end time 1111-11-11
        lt:str: encryption salt
        request_session:requests.Session: session to be maintained
        data:list: query result received from the server
        """
        self.username = ''
        self.password = ''
        self.start_time = ''
        self.end_time = ''
        self.lt = ''
        self.request_session = requests.Session()
        self.data = []

    def get_info(self):
        if self.username and self.password and self.start_time and self.end_time:
            re = input(
                'You have synchronized once.\nDo you want to Synchronize Again[S] Change Username and Password [C] Modify Query [M] Start a New Session [Press Any Other Key]? >>> ')
            if re == 'S' or re == 's':
                return
            elif re == 'C' or re == 'c':
                self.username = input('plz input your username >>> ')
                self.password = input('plz input your password >>> ')
                return
            elif re == 'M' or re == 'm':
                self.start_time = input('from (eg. 2020-03-20) >>> ')
                self.end_time = input('to (eg. 2020-04-20) >>> ')
                return
        self.username = input('plz input your username >>> ')
        self.password = input('plz input your password >>> ')
        self.start_time = input('from (eg. 2020-03-20) >>> ')
        self.end_time = input('to (eg. 2020-04-20) >>> ')

    @staticmethod
    def __get_js():
        with open('./des.js', 'r', encoding='utf-8') as f:
            line = f.readline()
            htmlstr = ''
            while line:
                htmlstr += line
                line = f.readline()
        return htmlstr

    def __get_des_passwd(self):
        js_str = self.__get_js()
        ctx = execjs.compile(js_str)
        return ctx.call('strEnc', self.username + self.password + self.lt, '1', '2', '3')

    @add_process_bar
    def login(self):
        """
        login and maintain a session in order to
        be authenticated to fetch data later.

        the login process of HUST pass involves
        DES encryption. A javascript script copied
        from the website will generate the encrypted
        information required.
        """
        print('trying to get the login page...')
        response = self.request_session.get(LOGIN_URL)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.lt = soup.find(id='lt').attrs['value']
        rsa = self.__get_des_passwd()
        ul = len(self.username)
        pl = len(self.password)
        execution = 'e1s1'
        _eventId = 'submit'
        form_data = {
            'rsa': rsa,
            'ul': ul,
            'pl': pl,
            'execution': execution,
            '_eventId': _eventId
        }
        r = self.request_session.post(LOGIN_URL, data=form_data)

    @add_process_bar
    def query(self):
        """
        the server will return a json format data.
        """
        query_form = {'start': self.start_time, 'end': self.end_time}
        response = self.request_session.post(QUERY_URL, data=query_form)
        try:
            self.data = response.json()
        except:
            print('failed to fetch timetable. Try synchronizing again.')

    def save_query(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        session = Session()
        if not self.data:
            return
        for course in self.data:
            lesson = Lesson(course['start'], course['end'], course['title'], eval(course['txt'])['JSMC'])
            session.add(lesson)
        session.commit()
        session.close()

    def synchronize(self):
        self.get_info()
        print('Trying to authenticate...')
        self.login()
        print('Trying to get the timetable...')
        self.query()
        print('Saving data...')
        self.save_query()
