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



import LinkChecker
from App.ImageFile import ImageFile

def initialize(context):
    """ Initialize the LinkChecker product"""
    context.registerClass(
        LinkChecker.LinkChecker,
        constructors = (
        LinkChecker.manage_addLinkCheckerForm,
        LinkChecker.manage_addLinkChecker),
        icon = 'www/checker.gif'
      )

misc_ = {
  'logentry':ImageFile('www/logentry.gif', globals()),
}
