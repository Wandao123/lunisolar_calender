# -*- coding: utf-8 -*-

__author__ = 'Wandao123'
__date__ = '2021/10/25'

from bs4 import BeautifulSoup
from datetime import datetime
from enum import Enum
import requests
#from requests_html import HTMLSession
from typing import Dict, List, Tuple

class PhaseName(Enum):
    NewMoon = (0, '朔')
    FirstQuarter = (90, '上弦')
    FullMoon = (180, '望')
    LastQuarter = (270, '下弦')

    # 角度は切りの良い数値のみしか認めない。
    def __init__(self, longitude: int, japanese: str) -> None:
        self.Longitude = longitude
        self.Japanese = japanese

    def __new__(cls, longitude: int, japanese: str) -> 'PhaseName':
        obj = object.__new__(cls)
        obj._value_ = (longitude, japanese)
        cls._value2member_map_.update({longitude: obj, japanese: obj})
        return obj

# Ref: https://emotionexplorer.blog.fc2.com/blog-entry-325.html
class LunarPhase:
    def __init__(self, year: int) -> None:
        self.__dates: Dict['PhaseName', List['datetime']] = {phase: [] for phase in PhaseName}
        #url = 'https://eco.mtk.nao.ac.jp/koyomi/yoko/2020/rekiyou203.html'
        url = 'https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_p.cgi'
        html = requests.post(url, data={'year': str(year)})
        html.raise_for_status()
        html.encoding = html.apparent_encoding
        soup = BeautifulSoup(html.content, 'html.parser')
        for row in soup.table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0:
                self.__dates[PhaseName(columns[3].text)].append(datetime.fromisoformat(columns[0].text.replace('/', '-') + 'T' + columns[1].text + ':00'))

    @property
    def Dates(self) -> List['datetime']:
        return self.__dates
