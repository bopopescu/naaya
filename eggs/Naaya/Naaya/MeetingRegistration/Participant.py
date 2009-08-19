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
# The Initial Owner of the Original Code is European Environment
# Agency (EEA).  Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Valentin Dumitru, Eau de Web

from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime

def addParticipant(self, REQUEST):
    """ Adds a participant's profile"""
    from random import randrange
    #validation
    form_fields = [field.id for field in self.registration_form]
    newParticipant = Participant(form_fields, **REQUEST.form)
    id = str(randrange(1000000,9999999))
    self._setObject(id, newParticipant)
    #Redirect to confirmation / print


class Participant(SimpleItem):
    """ Defines the profile of a registered participant,
    based on the fields of the meeting registration form"""
    def __init__(self, form_fields, **kwargs):
        """ """
        for k in form_fields:
            if kwargs.has_key(k):
                setattr(self, k, kwargs[k])
            else:
                setattr(self, k, '')
            #procesari (date = datetime(v))

InitializeClass(Participant)