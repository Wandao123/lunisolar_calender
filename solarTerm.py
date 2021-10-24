# -*- coding: utf-8 -*-

__author__ = 'Wandao123'
__date__ = '2021/10/25'

from bs4 import BeautifulSoup
from datetime import datetime
from enum import Enum
import requests
from typing import Dict, List, Tuple

class SolarTermName(Enum):
    StartOfSpring = (315, '立春')
    RainWater = (330, '雨水')
    AwakeningOfInsects = (345, '啓蟄')
    VernalEquinox = (0, '春分')
    ClearAndBright = (15, '清明')
    GrainRain = (30, '穀雨')
    StartOfSummer = (45, '立夏')
    SmallFull = (60, '小満')
    GrainInEar = (75, '芒種')
    SummerSolstice = (90, '夏至')
    MinorHeat = (105, '小暑')
    MajorHeat = (120, '大暑')
    StartOfAutumn = (135, '立秋')
    LimitOfHeat = (150, '処暑')
    WhiteDew = (165, '白露')
    AutumnalEquinox = (180, '秋分')
    ColdDew = (195, '寒露')
    FrostDescent = (210, '霜降')
    StartOfWinter = (225, '立冬')
    MinorSnow = (240, '小雪')
    MajorSnow = (255, '大雪')
    WinterSolstice = (270, '冬至')
    MinorCold = (285, '小寒')
    MajorCold = (300, '大寒')

    def __init__(self, longitude: int, japanese: str) -> None:
        self.Longitude = longitude
        self.Japanese = japanese

    def __new__(cls, longitude: int, japanese: str) -> 'SolarTermName':
        obj = object.__new__(cls)
        obj._value_ = (longitude, japanese)
        cls._value2member_map_.update({longitude: obj, japanese: obj})
        return obj

    # 中気の判定。
    @classmethod
    def IsEven(cls, name: 'SolarTermName') -> bool:
        return True if (name.Longitude // 15) % 2 == 0 else False

# Ref: https://emotionexplorer.blog.fc2.com/blog-entry-325.html
class SolarTerm:
    def __init__(self, year: int) -> None:
        self.__dates: Dict['SolarTermName', 'datetime'] = {}
        url = 'https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_s.cgi'
        html = requests.post(url, data={'year': str(year)})  # チェックボックスを外す方法？
        html.raise_for_status()
        html.encoding = html.apparent_encoding
        soup = BeautifulSoup(html.content, 'html.parser')
        for row in soup.table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0 and columns[3].text == '二十四節気':
                self.__dates[SolarTermName(columns[5].text[:2])] = datetime.fromisoformat(columns[0].text.replace('/', '-') + 'T' + columns[1].text + ':00')

    @property
    def Dates(self) -> Dict['SolarTermName', 'datetime']:
        return self.__dates
