# -*- coding: utf-8 -*-

__author__ = 'Wandao123'
__date__ = '2021/10/25'

from bs4 import BeautifulSoup
import datetime as dt
from enum import Enum
import numpy as np
import pandas as pd
import requests
#from requests_html import HTMLSession
from typing import Dict, List, Tuple

# Ref: https://qiita.com/cohey0727/items/a1179db49a4f40a3b7c4
# Ref: https://qiita.com/azumagoro/items/bafed453e12b7a5d4b2f
class PhaseName(Enum):
    NewMoon = (0, '朔')
    FirstQuarter = (90, '上弦')
    FullMoon = (180, '望')
    LastQuarter = (270, '下弦')
    Null = (np.nan, '')

    # 角度は切りの良い数値のみしか認めない。
    def __init__(self, longitude: int, japanese: str) -> None:
        self.Longitude = longitude
        self.Japanese = japanese

    def __new__(cls, longitude: int, japanese: str) -> 'PhaseName':
        obj = object.__new__(cls)
        obj._value_ = (longitude, japanese)
        cls._value2member_map_.update({longitude: obj, japanese: obj})
        return obj

# ウェブスクレイピングで月相と二十四節気の日付を取得する。
# 今後数値計算で黄経を算出する場合は、そのクラスだけファイルを分けて、スクレイピングする代わりにデータを参照する形式にする積もり。

# Ref: https://emotionexplorer.blog.fc2.com/blog-entry-325.html
class LunarPhase:
    def __init__(self, year: int) -> None:
        self.__datesOf: Dict[PhaseName, List[dt.datetime]] = {phase: [] for phase in PhaseName if phase != PhaseName.Null}
        #url = 'https://eco.mtk.nao.ac.jp/koyomi/yoko/2020/rekiyou203.html'
        url = 'https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_p.cgi'
        html = requests.post(url, data={'year': str(year)})
        html.raise_for_status()
        html.encoding = html.apparent_encoding
        soup = BeautifulSoup(html.content, 'html.parser')
        for row in soup.table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0:
                self.__datesOf[PhaseName(columns[3].text)].append(dt.datetime.fromisoformat(columns[0].text.replace('/', '-') + 'T' + columns[1].text + ':00'))

    @property
    def DatesOf(self) -> Dict[PhaseName, List[dt.datetime]]:
        return self.__datesOf

class TermName(Enum):
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
    Null = (np.nan, '')

    def __init__(self, longitude: int, japanese: str) -> None:
        self.Longitude = longitude
        self.Japanese = japanese

    def __new__(cls, longitude: int, japanese: str) -> 'TermName':
        obj = object.__new__(cls)
        obj._value_ = (longitude, japanese)
        cls._value2member_map_.update({longitude: obj, japanese: obj})
        return obj

    # 中気の判定。
    @classmethod
    def IsEven(cls, name: 'TermName') -> bool:
        if name == cls.Null:
            return False
        else:
            return True if (name.Longitude // 15) % 2 == 0 else False

# Ref: https://emotionexplorer.blog.fc2.com/blog-entry-325.html
class SolarTerm:
    def __init__(self, year: int) -> None:
        self.__dateOf: Dict[TermName, dt.datetime] = {}
        url = 'https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_s.cgi'
        html = requests.post(url, data={'year': str(year)})  # チェックボックスを外す方法？
        html.raise_for_status()
        html.encoding = html.apparent_encoding
        soup = BeautifulSoup(html.content, 'html.parser')
        for row in soup.table.find_all('tr'):
            columns = row.find_all('td')
            if len(columns) > 0 and columns[3].text == '二十四節気':
                self.__dateOf[TermName(columns[5].text[:2])] = dt.datetime.fromisoformat(columns[0].text.replace('/', '-') + 'T' + columns[1].text + ':00')

    @property
    def DateOf(self) -> Dict[TermName, dt.datetime]:
        return self.__dateOf

# Ref: https://hogehuga.com/post-1235/
class DataName(Enum):  # pandasのDataFrameの各項目。日本語との対応も兼ねる。
    SolarDate = (0, '太陽暦')
    LunarPhase = (1, '月相')
    SolarTerm = (2, '二十四節気')
    LunarDay = (3, '日')
    LunarMonth = (4, '月')
    IsLeap = (5, '閏')
    LunarYear = (6, '年')

    def __init__(self, value: int, japanese: str) -> None:
        self.Japanese = japanese

    def __new__(cls, value: int, japanese: str) -> 'DataName':
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

class Calender:
    def __init__(self, year: int) -> None:
        self.__previousLunarPhase = LunarPhase(year - 1)
        self.__currentLunarPhase = LunarPhase(year)
        self.__previousSolarTerm = SolarTerm(year - 1)
        self.__currentSolarTerm = SolarTerm(year)
        start: dt.datetime
        end: dt.datetime
        start, end = self.__calcDateRange()
        self.__dataFrame = pd.DataFrame(
            [],
            index=pd.date_range(start=start.date(), end=end.date(), name=DataName.SolarDate),
            columns=[name for name in DataName if name != DataName.SolarDate]
        )
        self.__fillLunarPhase()
        self.__fillSolarTerm()

    def __calcDateRange(self) -> Tuple[dt.datetime]:
        newMoonDates: List[dt.datetime] =\
            self.__previousLunarPhase.DatesOf[PhaseName.NewMoon]\
            + self.__currentLunarPhase.DatesOf[PhaseName.NewMoon]\
            + [self.__currentLunarPhase.DatesOf[PhaseName.NewMoon][-1] + dt.timedelta(days=30)]  # 翌年の朔月が未定なので、30日後（一箇月は29日間か30日間）を仮の朔月とする。
        start: dt.datetime = None  # 昨年の冬至を含む月（陰暦の意味）の朔日。
        end: dt.datetime = None  # 作成する年の冬至を含む月（陰暦の意味）の翌月の朔日。
        for i in range(len(newMoonDates) - 1):
            if newMoonDates[i] <= self.__previousSolarTerm.DateOf[TermName.WinterSolstice] < newMoonDates[i + 1]:
                start = newMoonDates[i]
            if newMoonDates[i] <= self.__currentSolarTerm.DateOf[TermName.WinterSolstice] < newMoonDates[i + 1]:
                end = newMoonDates[i + 1]
        return start, end

    def __fillLunarPhase(self):
        self.__dataFrame.loc[:, DataName.LunarPhase] = PhaseName.Null
        for phaseName in PhaseName:
            previous: List[dt.datetime] = self.__previousLunarPhase.DatesOf.get(phaseName)
            current: List[dt.datetime] = self.__currentLunarPhase.DatesOf.get(phaseName)
            if previous and current:
                previous = [datetime for datetime in previous if datetime >= self.__dataFrame.index.to_pydatetime()[0]]
                #current = [datetime for datetime in current if datetime <= self.__dataFrame.index.to_pydatetime()[-1]]  # 今年の月相の日付は必ず範囲内。
                self.__dataFrame.loc[map(lambda datetime: datetime.date().isoformat(), previous + current), DataName.LunarPhase] = phaseName
        self.__dataFrame.iloc[-1][DataName.LunarPhase] = PhaseName.NewMoon

    def __fillSolarTerm(self):
        self.__dataFrame.loc[:, DataName.SolarTerm] = TermName.Null
        self.__dataFrame.loc[map(lambda datetime: datetime.date().isoformat(), self.__currentSolarTerm.DateOf.values()), DataName.SolarTerm] = list(self.__currentSolarTerm.DateOf.keys())
        self.__dataFrame.at[self.__previousSolarTerm.DateOf[TermName.WinterSolstice].date().isoformat(), DataName.SolarTerm] = TermName.WinterSolstice

    def LunarDate(self, date: dt.date) -> Dict[str, int]:
        raw = self.__dataFrame.loc[date.isoformat()]
        return {
            'day': raw[DataName.LunarDay],
            'month': raw[DataName.LunarMonth],
            'leap': 1 if raw[DataName.IsLeap] else 0,
            'year': raw[DataName.LunarYear]
        }

    def Write(self, filename: str='') -> None:
        temp: pd.DataFrame = self.__dataFrame.copy()
        #temp[DataName.LunarPhase] = temp[DataName.LunarPhase].map(lambda lunarPhase: lunarPhase.Japanese)
        #temp[DataName.SolarTerm] = temp[DataName.SolarTerm].map(lambda solarTerm: solarTerm.Japanese)
        temp.loc[:, DataName.LunarPhase:DataName.SolarTerm] = temp.loc[:, DataName.LunarPhase:DataName.SolarTerm].applymap(lambda cell: cell.Japanese)
        temp.rename(columns=lambda dataName: dataName.Japanese, inplace=True)
        temp.index.rename(DataName.SolarDate.Japanese, inplace=True)
        if filename:
            temp.to_csv(filename, encoding='utf_8_sig')
        else:
            print(temp)