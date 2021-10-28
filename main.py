#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Wandao123'
__date__ = '2021/10/26'

import datetime as dt
import lunisolar

if __name__ == '__main__':
    for date in lunisolar.SolarTerm(2018, 2020, lunisolar.SolarTerm.Mode.SpaceDividingMethod).DatesOf.items():
        print(date)
    print()
    for date in lunisolar.SolarTerm(2018, 2020, lunisolar.SolarTerm.Mode.TimeDividingMethod).DatesOf.items():
        print(date)
    #calender = lunisolar.Calender(2020)
    #calender.Write('lunisolar_calender.csv')