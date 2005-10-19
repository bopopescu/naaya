# The contents of this file are subject to the Mozilla Public
# License Version 1.1 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of
# the License at http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS
# IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
# implied. See the License for the specific language governing
# rights and limitations under the License.
#
# Portions created by EEA are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Ghica, Finsiel Romania

__version__='$Revision: 1.24 $'[11:-2]

# python imports
from time import localtime, mktime, strftime

#Zope import
from DateTime import DateTime


class DateFunctions:
    """ date functions """

    def __init__(self):
        """ constructor """
        pass


    #################
    #   CONSTANTS   #
    #################

    LongWeekdays = {"0":"Monday",
                    "1":"Tuesday",
                    "2":"Wednesday",
                    "3":"Thursday",
                    "4":"Friday",
                    "5":"Saturday",
                    "6":"Sunday"}
    day_name_length =['1', '2', '3', 'All']
    mdays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


    ###############
    #   GETTERS   #
    ###############

    def getCurrentYear(self):
        """ return current year """
        return DateTime().year()

    def getCurrentMonth(self):
        """ return current month """
        return DateTime().month()

    def getCurrentDay(self):
        """ return current day """
        return DateTime().day()

    def getShortWeekdays(self, p_length):
        """."""
        return self.utGenerateList(self.getDayIndex(self.start_day), self.utDayLength(p_length))

    def LongMonths(self, p_index):
        """ return the month's name """
        setTranslation = self.getSite().getPortalTranslations().translate
        if p_index == 0:
            return setTranslation('', 'January')
        elif p_index == 1:
            return setTranslation('', 'February')
        elif p_index == 2:
            return setTranslation('', 'March')
        elif p_index == 3:
            return setTranslation('', 'April')
        elif p_index == 4:
            return setTranslation('', 'May')
        elif p_index == 5:
            return setTranslation('', 'June')
        elif p_index == 6:
            return setTranslation('', 'July')
        elif p_index == 7:
            return setTranslation('', 'August')
        elif p_index == 8:
            return setTranslation('', 'September')
        elif p_index == 9:
            return setTranslation('', 'October')
        elif p_index == 10:
            return setTranslation('', 'November')
        elif p_index == 11:
            return setTranslation('', 'December')

    def LongDays(self, p_index):
        """ return the day's name """
        setTranslation = self.getSite().getPortalTranslations().translate
        if p_index == 0:
            return setTranslation('', 'Monday')
        elif p_index == 1:
            return setTranslation('', 'Tuesday')
        elif p_index == 2:
            return setTranslation('', 'Wednesday')
        elif p_index == 3:
            return setTranslation('', 'Thursday')
        elif p_index == 4:
            return setTranslation('', 'Friday')
        elif p_index == 5:
            return setTranslation('', 'Saturday')
        elif p_index == 6:
            return setTranslation('', 'Sunday')

    def getLongWeekdays(self):
        """ return long weekdays """
        l_LongWeekdays={}
        for i in range(7):
            l_LongWeekdays[str(i)]=self.LongDays(i)
        return l_LongWeekdays

    def getLongWeekdaysSorted(self):
        """ return long day's name sorted """
        return self.sortedDictByKey(self.getLongWeekdays())

    def getDayIndex(self, p_day):
        """ return the day index """
        for key in self.getLongWeekdays().keys():
            if self.getLongWeekdays()[key] == p_day:  return int(key)

    def getDayLengths(self):
        """ return the choises for day length """
        l_length = []
        l_length.extend(self.day_name_length)
        return l_length

    #################
    #   FUNCTIONS   #
    #################

    def testCurrentDay(self, p_day, p_month, p_year):
        """ test if current day """
        if self.getCurrentDay()==p_day and self.getCurrentMonth()==int(p_month) and int(self.getCurrentYear())==int(p_year):
            return 1
        return 0

    def getNextDate(self, p_month, p_year):
        """ return next month """
        if int(p_month) < 12:
            return (int(p_month)+1, int(p_year))
        else:
            return (1, int(p_year)+1)

    def getPrevDate(self, p_month, p_year):
        """ return last month """
        if int(p_month) > 1:
            return (int(p_month)-1, int(p_year))
        else:
            return (12, int(p_year)-1)

    def getMonthName(self, p_month):
        """ reurns the month's name """
        return self.LongMonths(int(p_month)-1)

    def getYear(self, p_date):
        """ return year from a given date """
        l_date = str(p_date)
        if l_date != '':
            try:    return str(DateTime(l_date).year())
            except: return ''
        else:       return ''

    def getMonth(self, p_date):
        """ return month from a given date """
        l_date = str(p_date)
        if l_date != '':
            try:    return str(DateTime(l_date).month())
            except: return ''
        else:       return ''

    def getDay(self, p_date):
        """ return day from a given date """
        l_date = str(p_date)
        if l_date != '':
            try:    return str(DateTime(l_date).day())
            except: return ''
        else:       return ''

    def getDate(self, p_date):
        """ return date """
        setTranslation = self.getSite().getPortalTranslations().translate
        l_date = str(p_date)
        if l_date != '':
            try:    return DateTime(l_date).strftime("%d %B %Y")
            except: return setTranslation('', 'empty')
        else:       return setTranslation('', 'empty')

    def isLeapYear(self, year):
        """ return 1 for leap years, 0 for non-leap years """
        return year % 4 == 0 and (year % 100 <> 0 or year % 400 == 0)

    def getWeekday(self, year, month, day):
        """ return weekday (0-6 ~ Mon-Sun) for year (1970-...), month (1-12), day (1-31) """
        secs = mktime((year, month, day, 0, 0, 0, 0, 0, 0))
        tuple = localtime(secs)
        return tuple[6]

    def getMonthRange(self, year, month):
        """ return weekday (0-6 ~ Mon-Sun) and number of days (28-31) for year, month """
        if not 1 <= int(month) <= 12: raise ValueError, 'bad month number'
        day1 = self.getWeekday(int(year), int(month), 1)
        ndays = self.mdays[int(month)] + (int(month) == 2 and self.isLeapYear(int(year)))
        return day1, ndays

#    def dfConvStrToDateTimeObj(self, p_datestring, p_separator='/'):
#        """Takes a string that represents a date like 'dd/mm/yyyy' and returns a DateTime object"""
#        if p_datestring != '':
#            l_dateparts = p_datestring.split(p_separator)
#            l_intYear = int(l_dateparts[2], 10)
#            l_intMonth = int(l_dateparts[1], 10)
#            l_intDay = int(l_dateparts[0], 10)
#            return DateTime(str(l_intYear) + '/' + str(l_intMonth) + '/' + str(l_intDay) + ' 00:00:00')
#        else:
#            return None