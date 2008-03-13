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
__version__ = '''$Revision$'''

import urllib

class MyURLopener(urllib.FancyURLopener):

    http_error_default = urllib.URLopener.http_error_default

    version = "Naaya Link Checker/%s" % __version__

    def __init__(self, *args, **kw):
        urllib.FancyURLopener.__init__(self, *args, **kw)

    def http_error_401(self, url, fp, errcode, errmsg, headers):
        return self.http_error_default(url, fp, errcode, errmsg, headers)
