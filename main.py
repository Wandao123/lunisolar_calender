#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Wandao123'
__date__ = '2021/10/26'

import datetime as dt
import lunisolar

if __name__ == '__main__':
    calender = lunisolar.Calender(2020)
    for delta in range(10):
        date = dt.date(2020, 1, 1) + dt.timedelta(days=delta)
        print(calender.LunarDate(date))