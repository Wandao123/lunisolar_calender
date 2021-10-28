#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Wandao123'
__date__ = '2021/10/26'

import datetime as dt

from pandas.core.indexes.datetimes import date_range
import lunisolar

if __name__ == '__main__':
    calender = lunisolar.Calender(2017, 2021)
    calender.Write('lunisolar_calender.csv')
