# -*- coding: utf-8 -*-

__author__ = 'Wandao123'
__date__ = '2021/10/25'

from bs4 import BeautifulSoup
import datetime as dt
from enum import Enum, auto
import numpy as np
import pandas as pd
import requests
#from requests_html import HTMLSession
from typing import Dict, List, Tuple, FrozenSet

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
    def __init__(self, beginningYear: int, endingYear: int) -> None:
        self.__datesOf: Dict[PhaseName, List[dt.datetime]] = {phase: [] for phase in PhaseName if phase != PhaseName.Null}
        #url = 'https://eco.mtk.nao.ac.jp/koyomi/yoko/2020/rekiyou203.html'
        url = 'https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_p.cgi'
        for year in range(beginningYear, endingYear + 1):
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
    class Mode(Enum):
        TimeDividingMethod = auto()
        SpaceDividingMethod = auto()

    def __init__(self, beginningYear: int, endingYear: int, mode: Mode) -> None:
        self.__datesOf: Dict[TermName, List[dt.datetime]] = {term: [] for term in TermName if term != TermName.Null}
        url = 'https://eco.mtk.nao.ac.jp/cgi-bin/koyomi/cande/phenomena_s.cgi'
        if mode == self.Mode.TimeDividingMethod:
            for year in range(beginningYear - 1, endingYear + 1):
                html = requests.post(url, data={'year': str(year)})  # チェックボックスを外す方法？――BeautifulSoupのみでは不可。
                html.raise_for_status()
                html.encoding = html.apparent_encoding
                soup = BeautifulSoup(html.content, 'html.parser')
                for row in soup.table.find_all('tr'):
                    columns = row.find_all('td')
                    if len(columns) > 0 and columns[5].text[:2] == '冬至':
                        self.__datesOf[TermName.WinterSolstice].append(dt.datetime.fromisoformat(columns[0].text.replace('/', '-') + 'T' + columns[1].text + ':00'))
            for year in range(beginningYear, endingYear + 1):
                previous: dt.datetime
                current: dt.datetime
                #previous, current = [date for date in sorted(self.__datesOf[TermName.WinterSolstice]) if date.year == year - 1 or date.year == year]
                previous, current = sorted(list(filter(lambda date: date.year == year - 1 or date.year == year, self.__datesOf[TermName.WinterSolstice])))
                delta = (current - previous) / 24
                for i in range(1, 24):
                    self.__datesOf[TermName((15 * i + TermName.WinterSolstice.Longitude) % 360)].append(previous + i * delta)
            # 定気法に合わせるために、余分に取得した冬至を削除しているが、むしろ「昨年の冬至から今年の冬至まで」という仕様にするべき？
            self.__datesOf[TermName.WinterSolstice] = list(filter(lambda date: date.year >= beginningYear, self.__datesOf[TermName.WinterSolstice]))
        elif mode == self.Mode.SpaceDividingMethod:
            for year in range(beginningYear, endingYear + 1):
                html = requests.post(url, data={'year': str(year)})  # チェックボックスを外す方法？――BeautifulSoupのみでは不可。
                html.raise_for_status()
                html.encoding = html.apparent_encoding
                soup = BeautifulSoup(html.content, 'html.parser')
                for row in soup.table.find_all('tr'):
                    columns = row.find_all('td')
                    if len(columns) > 0 and columns[3].text == '二十四節気':
                        self.__datesOf[TermName(columns[5].text[:2])].append(dt.datetime.fromisoformat(columns[0].text.replace('/', '-') + 'T' + columns[1].text + ':00'))
        else:
            raise TypeError(str(mode.value) + ' is not included in the Mode type.')

    @property
    def DatesOf(self) -> Dict[TermName, List[dt.datetime]]:
        return self.__datesOf

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
        self.__lunarPhase = LunarPhase(year - 1, year)
        self.__solarTerm = SolarTerm(year - 1, year)
        start: dt.datetime
        end: dt.datetime
        start, end = self.__calcDateRange()
        self.__dataFrame = pd.DataFrame(
            [],
            index=pd.date_range(start=start.date(), end=end.date(), name=DataName.SolarDate),
            columns=[name for name in DataName if name != DataName.SolarDate]
        )
        self.__fillLunarPhases()
        self.__fillSolarTerms()
        self.__fillLunarDates()
        self.__dataFrame.drop(self.__dataFrame.index[[-1]], inplace=True)  # 最後の行はダミーなので削除。

    def __calcDateRange(self) -> Tuple[dt.datetime]:
        newMoonDates: List[dt.datetime] =\
            self.__lunarPhase.DatesOf[PhaseName.NewMoon]\
            + [self.__lunarPhase.DatesOf[PhaseName.NewMoon][-1] + dt.timedelta(days=29)]  # 翌年の朔月が未定なので、30日後（一箇月は29日間か30日間）を仮の朔月とする。
        start: dt.datetime = None  # 昨年の冬至を含む月（陰暦の意味）の朔日。
        end: dt.datetime = None  # 作成する年の冬至を含む月（陰暦の意味）の翌月の朔日。
        firstWinterSolstice: dt.datetime = min(self.__solarTerm.DatesOf[TermName.WinterSolstice])
        lastWinterSolstice: dt.datetime = max(self.__solarTerm.DatesOf[TermName.WinterSolstice])
        for i in range(len(newMoonDates) - 1):
            if newMoonDates[i] <= firstWinterSolstice< newMoonDates[i + 1]:
                start = newMoonDates[i]
            if newMoonDates[i] <= lastWinterSolstice < newMoonDates[i + 1]:
                end = newMoonDates[i + 1]
        return start, end

    def __fillLunarPhases(self):
        self.__dataFrame.loc[:, DataName.LunarPhase] = PhaseName.Null
        for phaseName in PhaseName:
            dates: List[dt.datetime] = self.__lunarPhase.DatesOf.get(phaseName)
            if dates:
                dates = [datetime for datetime in dates if self.__dataFrame.index[0].to_pydatetime() <= datetime < self.__dataFrame.index[-1].to_pydatetime()]
                self.__dataFrame.loc[map(lambda datetime: datetime.date().isoformat(), dates), DataName.LunarPhase] = phaseName
        self.__dataFrame.iloc[-1][DataName.LunarPhase] = PhaseName.NewMoon  # 最終日はダミー（番兵として加える）。

    def __fillSolarTerms(self):
        self.__dataFrame.loc[:, DataName.SolarTerm] = TermName.Null
        for termName in TermName:
            dates: List[dt.datetime] = self.__solarTerm.DatesOf.get(termName)
            if dates:
                dates = [datetime for datetime in dates if self.__dataFrame.index[0].to_pydatetime() <= datetime < self.__dataFrame.index[-1].to_pydatetime()]
                self.__dataFrame.loc[map(lambda datetime: datetime.date().isoformat(), dates), DataName.SolarTerm] = termName

    def __fillLunarDates(self):
        df = self.__dataFrame  # 長いので通称を付ける。
        newMoonIndices: pd.DatetimeIndex = df[df[DataName.LunarPhase] == PhaseName.NewMoon].index
        evenSolarTerm: FrozenSet[SolarTerm] = frozenset({termName for termName in TermName if TermName.IsEven(termName)})
        month: int = -36  # 想定外の処理が発生した場合に備えて、有り得ない値を初期値に設定。
        isLeap: bool = False
        year: int = df.index[0].year  # 表の期間の作り方から、必ず太陽暦と太陰太陽暦の年は一致する。
        for i in range(newMoonIndices.size - 1):
            oneMonthPeriod: np.ndarray[float] = (df.index >= newMoonIndices[i]) & (df.index < newMoonIndices[i + 1])
            df.loc[oneMonthPeriod, DataName.LunarDay] = [day + 1 for day in range((newMoonIndices[i + 1] - newMoonIndices[i]).days)]
            if df.loc[oneMonthPeriod, DataName.SolarTerm].isin({TermName.WinterSolstice}).any():
                month = 11
                isLeap = False
            elif df.loc[oneMonthPeriod, DataName.SolarTerm].isin({TermName.VernalEquinox}).any():
                month = 2
                isLeap = False
            elif df.loc[oneMonthPeriod, DataName.SolarTerm].isin({TermName.SummerSolstice}).any():
                month = 5
                isLeap = False
            elif df.loc[oneMonthPeriod, DataName.SolarTerm].isin({TermName.AutumnalEquinox}).any():
                month = 8
                isLeap = False
            elif df.loc[oneMonthPeriod, DataName.SolarTerm].isin(evenSolarTerm).any():
                if month >= 12:  # yearも更新しなければならないため、剰余で書けない。
                    month = 1
                    year += 1
                else:
                    month += 1
                isLeap = False
            else:
                if (~df.loc[df.index < newMoonIndices[i], DataName.IsLeap]).all():  # その年の最初の閏月か？
                    isLeap = True
                else:
                    isLeap = False
            df.loc[oneMonthPeriod, DataName.LunarMonth] = month
            df.loc[oneMonthPeriod, DataName.IsLeap] = isLeap
            df.loc[oneMonthPeriod, DataName.LunarYear] = year

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
        temp.loc[:, DataName.LunarPhase:DataName.SolarTerm] = temp.loc[:, DataName.LunarPhase:DataName.SolarTerm].applymap(lambda cell: cell.Japanese)
        temp.rename(columns=lambda dataName: dataName.Japanese, inplace=True)
        temp.index.rename(DataName.SolarDate.Japanese, inplace=True)
        if filename:
            temp.to_csv(filename, encoding='utf_8_sig')
        else:
            print(temp)