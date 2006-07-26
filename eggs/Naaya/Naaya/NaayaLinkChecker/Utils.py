#The contents of this file are subject to the Mozilla Public
#License Version 1.1 (the "License"); you may not use this file
#except in compliance with the License. You may obtain a copy of
#the License at http://www.mozilla.org/MPL/
#
#Software distributed under the License is distributed on an "AS
#IS" basis, WITHOUT WARRANTY OF ANY KIND, either express or
#implied. See the License for the specific language governing
#rights and limitations under the License.
#
#The Original Code is "LinkChecker"
#
#The Initial Owner of the Original Code is European Environment
#Agency (EEA).  Portions created by Finsiel Romania are
#Copyright (C) 2006 by European Environment Agency.  All
#Rights Reserved.
#
#Contributor(s):
#  Original Code: Cornel Nitu (Finsiel Romania)


import string
from Products.PythonScripts.standard import url_quote
import re
from whrandom import choice
from DateTime import DateTime

class UtilsManager:
    """UtilsManager class"""

    def __init__(self):
        """Constructor"""
        pass

    def umGetROOT(self):
        """ get the ROOT object"""
        return self.unrestrictedTraverse(('',))

    def umGenRandomKey(self, length=10, chars=string.digits):
        """Generate a random numeric key."""
        return ''.join([choice(chars) for i in range(length)])

    def umConvertToList(self, something):
        """Convert to list"""
        ret = something
        if type(something) is type(''):
            ret = [something]
        return ret

    def umFormatDateTimeToString(self, date):
        """Gets a date (tuple - (yyyy, mm, dd, hh, mm, ss, 3, 311, 0)) and returns a string like dd/mm/yyyy hh:mm:ss"""
        year = str(date[0])
        month = str(date[1])
        if len(month)==1:
            month = '0' + month
        day = str(date[2])
        if len(day)==1:
            day = '0' + day
        hours = str(date[3])
        if len(hours)==1:
            hours = '0' + hours
        minutes = str(date[4])
        if len(minutes)==1:
            minutes = '0' + minutes
        return day + '/' + month + '/' + year + ' ' + hours + ':' + minutes

    def umGetTodayDate(self):
        """Returns today date in a DateTime object"""
        return DateTime()

    #############
    # ENCODING  #
    #############

    def umURLEncode(self, str):
        """Encode a string using url_encode"""
        return url_quote(str)

    #################
    # PARSING STUFF #
    #################

    def parseUrls(self, text):
        """Given a text string, returns all the urls we can find in it."""
        urls = '(?: %s)' % '|'.join("http https telnet gopher file wais ftp".split())
        ltrs = r'\w'
        gunk = r'/#~:.?+=&%@!\-'
        punc = r'.:?\-'
        any = "%(ltrs)s%(gunk)s%(punc)s" % { 'ltrs':ltrs, 'gunk':gunk, 'punc':punc}
        url = r'\b%(urls)s:[%(any)s]+?(?=[%(punc)s]*(?:   [^%(any)s]|$))' % {'urls':urls, 'any':any, 'punc':punc}
        url_re = re.compile(url, re.VERBOSE | re.MULTILINE)
        return url_re.findall(text)

    def getItemTitle(self, url, size=20):
        """ return the object by url """
        try:
            obj_title = self.unrestrictedTraverse(url).title_or_id()
            if size == 0:
                return obj_title
            if len(obj_title) > size:
                return '%s...' % obj_title[:size]
        except KeyError:
            return None