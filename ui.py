# -*- coding: utf-8 -*-
# @Time    : 2020/3/31 23:47
# @Author  : Edgar Tang
# @Email   : tctco001@gmail.com
# @File    : ui.py
# @Software: PyCharm

import os
from datetime import datetime, timedelta
from prettytable import PrettyTable
from pynput import keyboard
import time

from database import Lesson
from database import Session
from Synchronizer import Synchronizer
from constants import MAX_LENGTH

display_date = datetime.now().date()
mode = 'name'
f_synchronize = False
f_exit = False
this_week = datetime.now().isocalendar()[1]


def draw_table(week, mode='name'):
    """
    draw a pretty timetable according to week and mode
    and a greeting string according to local time
    :param week:int: iso week number
    :param mode:str: 'name': render class name
                     'location':render class location
    """
    if this_week == week:
        today = datetime.now().isocalendar()[2]
    else:
        today = None
    tb = PrettyTable()
    tb.add_column('', [str(x + 1) for x in range(4)] + ['----'] + [str(x + 1) for x in range(4, 12)])
    session = Session()
    for day in range(1, 8):
        lessons = session.query(Lesson).filter_by(week=week, weekday=day).all()
        l = ['-' for _ in range(12)]
        for lesson in lessons:
            pointer = lesson.index - 1
            while l[pointer] != '-':
                pointer += 1
            if mode == 'location':
                l[pointer] = lesson.location
            else:
                l[pointer] = lesson.name if len(lesson.name) <= MAX_LENGTH else lesson.name[: MAX_LENGTH - 1] + '..'
        l.insert(4, '-----')
        if today == day:
            tb.add_column('TODAY', l)
        else:
            tb.add_column(str(day), l)
    session.close()

    os.system('cls')
    time = datetime.now().strftime('%Y-%m-%d %H:%M:%S %A')
    print(time)
    print_greetings(time)
    print(tb)

    start = display_date - timedelta(days=display_date.isocalendar()[2] - 1)
    end = start + timedelta(days=7)
    print(str(start) + ' to ' + str(end))


def print_greetings(str_time):
    hour = str_time.split()[1].split(':')[0]
    if hour <= '05':
        greetings = 'It\'s late at time, you have done a great job today...'
    elif '05' < hour <= '09':
        greetings = 'Bonjour! Have a nice day!'
    elif '09' < hour <= '12':
        greetings = 'Wonder what\'s the next class?'
    elif '12' < hour <= '17':
        greetings = 'Something wonderful is about to happen :)'
    else:
        greetings = 'Today is great, isn\'t it?'
    print(greetings)


def on_press(key):
    global display_date, mode, f_exit, f_synchronize
    if key == keyboard.Key.right:
        display_date += timedelta(days=7)
        display_week = display_date.isocalendar()[1]
        draw_table(display_week)
    elif key == keyboard.Key.left:
        display_date -= timedelta(days=7)
        display_week = display_date.isocalendar()[1]
        draw_table(display_week)
    elif key == keyboard.Key.up:
        if mode == 'location':
            return
        mode = 'location'
        display_week = display_date.isocalendar()[1]
        draw_table(display_week, mode)
    elif key == keyboard.Key.shift:
        time.sleep(0.1)
        f_synchronize = True
        return False
    elif key == keyboard.Key.space:
        display_date = datetime.now().date()
        display_week = display_date.isocalendar()[1]
        draw_table(display_week)
    elif key == keyboard.Key.esc:
        f_exit = True
        return False
    else:
        try:
            if key.char == 'h':
                os.system('cls')
                print(
                    'Synchronize [shift]\tExit [esc]\tLast Week [left]\n'
                    'Next Week [Right]\tLocation [up]\tGoto Today [space]')
                input('press any key to go back to the main page >>> ')
                display_week = display_date.isocalendar()[1]
                draw_table(display_week)
        except:
            pass


def on_release(key):
    global display_date, mode
    if key == keyboard.Key.up:
        display_week = display_date.isocalendar()[1]
        mode = 'name'
        draw_table(display_week)


def start_ui():
    global f_synchronize
    synchronizer = Synchronizer()
    draw_table(this_week)
    print('Press [h] to see how to use')
    try:
        while not f_exit:
            with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
                listener.join()
            if f_synchronize:
                synchronizer.synchronize()
                draw_table(this_week)
                f_synchronize = False
    except:
        pass
