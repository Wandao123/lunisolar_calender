#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Wandao123'
__date__ = '2021/10/26'

import datetime as dt

from pandas.core.indexes.datetimes import date_range
import lunisolar

if __name__ == '__main__':
    calender = lunisolar.Calender(2021, lunisolar.Calender.Mode.Chinese, lunisolar.SolarTerm.Mode.TimeDividingMethod)
    calender.Write('lunisolar_calender.csv')