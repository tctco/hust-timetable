# -*- coding: utf-8 -*-
# @Time    : 2020/3/31 23:37
# @Author  : Edgar Tang
# @Email   : tctco001@gmail.com
# @File    : database.py
# @Software: PyCharm

from sqlalchemy import Column, Integer, String
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Lesson(Base):
    """
    This is a ORM model class.
    Params stored include:
    id:int: key
    name:str: course title
    start:str: class start time '00:00'
    end:str: class end time '00:00'
    location:str: class location
    date:str: class date '0000-00-00'
    week:int: iso calendar week, start from 1
    weekday:int: iso calendar weekday, 1 to 7
    index:int: The index of class in the day, eg. class at 08:00 has index 1 (first class in a day)
    """
    __tablename__ = 'lesson'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    start = Column('start', String)
    end = Column('end', String)
    location = Column('location', String)
    date = Column('date', String)
    week = Column('week', Integer)
    weekday = Column('weekday', Integer)
    index = Column('index', Integer)

    def __init__(self, start, end, name, location):
        self.date, self.start = start.split()
        self.end = end.split()[1]
        self.name = name
        self.location = location

        _, self.week, self.weekday = datetime.strptime(self.date, '%Y-%m-%d').isocalendar()
        if self.start == '08:00':
            self.index = 1
        elif self.start == '10:10':
            self.index = 3
        elif self.start == '14:00' or self.start == '14:30':
            self.index = 5
        elif self.start == '15:55' or self.start == '16:25':
            self.index = 7
        elif self.start == '18:30' or self.start == '19:00':
            self.index = 9
        elif self.start == '20:15' or self.start == '20:45':
            self.index = 10


engine = create_engine('sqlite:///lessons.db')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)
