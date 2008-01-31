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
# David Batranu, Eau de Web

#Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens, view
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Acquisition import Implicit
from OFS.Image import cookId

#Product imports
from Products.NaayaContent.constants import *
from Products.NaayaCore.managers.utils import utils
from Products.NaayaBase.constants import *
from Products.NaayaBase.NyContainer import NyContainer
from Products.NaayaBase.NyAttributes import NyAttributes
from Products.NaayaBase.NyCheckControl import NyCheckControl
from Products.NaayaBase.NyValidation import NyValidation
from Products.Localizer.LocalPropertyManager import LocalProperty
from Products.NaayaBase.NyProperties import NyProperties
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Products.NaayaContent.NyExFile.NyExFile import addNyExFile
from simpleconsultation_comment import addSimpleConsultationComment


#module constants
PERMISSION_REVIEW_SIMPLECONSULTATION = 'Review Simple Consultation'
PERMISSION_MANAGE_SIMPLECONSULTATION = 'Manage Simple Consultation'

METATYPE_OBJECT = 'Naaya Simple Consultation'
LABEL_OBJECT = 'Simple Consultation'
PERMISSION_ADD_OBJECT = 'Naaya - Add Naaya Simple Consultation objects'
OBJECT_FORMS = []
OBJECT_CONSTRUCTORS = ['manage_addNySimpleConsultation_html', 'simpleconsultation_add_html', 'addNySimpleConsultation']
OBJECT_ADD_FORM = 'simpleconsultation_add_html'
DESCRIPTION_OBJECT = 'This is Naaya Simple Consultation type.'
PREFIX_OBJECT = 'scns'
PROPERTIES_OBJECT = {
    'id':                  (0, '', ''),
    'title':               (1, MUST_BE_NONEMPTY, 'The Title field must have a value.'),
    'description':         (0, '', ''),
    'start_date':          (0, MUST_BE_DATETIME, 'The Start Date field must contain a valid date.'),
    'end_date':            (0, MUST_BE_DATETIME, 'The End Date field must contain a valid date.'),
    'sortorder':           (0, MUST_BE_POSITIV_INT, 'The Sort order field must contain a positive integer.'),
    'releasedate':         (0, MUST_BE_DATETIME, 'The Release date field must contain a valid date.'),
    'allow_file':          (0, '', ''),
    'public_registration': (0, '', ''),
    'lang':                (0, '', '')
}

manage_addNySimpleConsultation_html = PageTemplateFile('zpt/simpleconsultation_manage_add', globals())
manage_addNySimpleConsultation_html.kind = METATYPE_OBJECT
manage_addNySimpleConsultation_html.action = 'addNySimpleConsultation'

simpleconsultation_add_html = PageTemplateFile('zpt/simpleconsultation_add', globals())

def addNySimpleConsultation(self, id='', title='', description='', sortorder='', start_date='', end_date='', public_registration='', 
                            allow_file='', contributor=None, releasedate='', lang=None, REQUEST=None, **kwargs):
    """
    Create a Naaya Simple Consultation type of object.
    """
    #process parameters
    id = self.utCleanupId(id)
    if not id: id = self.utGenObjectId(title)
    try: sortorder = abs(int(sortorder))
    except: sortorder = DEFAULT_SORTORDER

    #check mandatory fiels
    l_referer = ''
    if REQUEST is not None: l_referer = REQUEST['HTTP_REFERER'].split('/')[-1]
    if not(l_referer == 'simpleconsultation_manage_add' or l_referer.find('simpleconsultation_manage_add') != -1) and REQUEST:
        r = self.getSite().check_pluggable_item_properties(METATYPE_OBJECT, id=id, title=title, sortorder=sortorder, \
            start_date=start_date, end_date=end_date, public_registration=public_registration)
    else:
        r = []
    if not len(r):
        #process parameters
        if contributor is None: contributor = self.REQUEST.AUTHENTICATED_USER.getUserName()
        if self.glCheckPermissionPublishObjects():
            approved, approved_by = 1, self.REQUEST.AUTHENTICATED_USER.getUserName()
        else:
            approved, approved_by = 0, None
        releasedate = self.process_releasedate(releasedate)
        if lang is None: lang = self.gl_get_selected_language()
        #check if the id is invalid (it is already in use)
        i = 0
        while self._getOb(id, None) is not None:
            i += 1
            id = '%s-%u' % (id, i)
        #create object
        ob = NySimpleConsultation(id, title, description, sortorder, start_date,
                                  end_date, public_registration, allow_file, contributor, releasedate, lang)
        self.gl_add_languages(ob)
        ob.createDynamicProperties(self.processDynamicProperties(METATYPE_OBJECT, REQUEST, kwargs), lang)
        self._setObject(id, ob)
        #extra settings
        ob = self._getOb(id)
        ob.submitThis()
        self.recatalogNyObject(ob)
        self.notifyFolderMaintainer(self, ob)
        #log post date
        auth_tool = self.getAuthenticationTool()
        auth_tool.changeLastPost(contributor)
        #redirect if case
        if REQUEST is not None:
            if l_referer == 'simpleconsultation_manage_add' or l_referer.find('simpleconsultation_manage_add') != -1:
                return self.manage_main(self, REQUEST, update_menu=1)
            elif l_referer == 'simpleconsultation_add_html':
                self.setSession('referer', self.absolute_url())
                REQUEST.RESPONSE.redirect('%s/messages_html' % self.absolute_url())
    else:
        if REQUEST is not None:
            self.setSessionErrors(r)
            self.set_pluggable_item_session(METATYPE_OBJECT, id=id, title=title, description=description, \
                sortorder=sortorder, releasedate=releasedate, start_date=start_date, end_date=end_date, 
                allow_file=allow_file, public_registration=public_registration, lang=lang)
            REQUEST.RESPONSE.redirect('%s/simpleconsultation_add_html' % self.absolute_url())
        else:
            raise Exception, '%s' % ', '.join(r)

class NySimpleConsultation(NyAttributes, Implicit, NyProperties, BTreeFolder2, NyContainer, NyCheckControl, NyValidation, utils):
    """ """

    meta_type = METATYPE_OBJECT
    meta_label = LABEL_OBJECT

    all_meta_types = ()

    icon = 'misc_/NaayaContent/NySimpleConsultation.gif'
    icon_marked = 'misc_/NaayaContent/NySimpleConsultation_marked.gif'

    title = LocalProperty('title')
    description = LocalProperty('description')

    security = ClassSecurityInfo()

    def __init__(self, id, title, description, sortorder, start_date, end_date, public_registration, allow_file, contributor, releasedate, lang):
        """ """
        self.id = id
        self.contributor = contributor
        NyValidation.__dict__['__init__'](self)
        NyCheckControl.__dict__['__init__'](self)
        NyContainer.__dict__['__init__'](self)
        BTreeFolder2.__init__(self)
        try: del self.title
        except: pass
        self.save_properties(title, description, sortorder, start_date, end_date, public_registration, allow_file, releasedate, lang)
        NyProperties.__dict__['__init__'](self)

    security.declarePrivate('save_properties')
    def save_properties(self, title, description, sortorder, start_date, end_date, public_registration, allow_file, releasedate, lang):
        
        self._setLocalPropValue('title', lang, title)
        self._setLocalPropValue('description', lang, description)
        
        if start_date:
            self.start_date = self.utConvertStringToDateTimeObj(start_date)
        else:
            self.start_date = self.utGetTodayDate()
            
        if end_date:
            self.end_date = self.utConvertStringToDateTimeObj(end_date)
        else:
            self.end_date = self.utGetTodayDate()
            
        self.sortorder = sortorder
        self.releasedate = releasedate
        self.public_registration = public_registration
        self.allow_file = allow_file

    security.declareProtected(PERMISSION_MANAGE_SIMPLECONSULTATION, 'saveProperties')
    def saveProperties(self, title='', description='', sortorder='', start_date='', end_date='',
                       public_registration='', allow_file='', file='', lang='', REQUEST=None):
        """ """
        
        if not title:
            self.setSession('title', title)
            self.setSession('description', description)
            self.setSessionErrors(['The Title field must have a value.'])
            return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        
        if file and not file.read():
            self.setSession('title', title)
            self.setSession('description', description)
            self.setSessionErrors(['File must not be empty'])
            return REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))
        
        exfile = self.get_exfile()
        
        if file and exfile:
            exfile.saveUpload(file=file, lang=lang)
            downloadfilename=file.filename
            exfile._setLocalPropValue('downloadfilename', lang, downloadfilename)
        elif file and not exfile:
            addNyExFile(self, title=title, file=file, lang=lang, source='file')
            
        releasedate = self.releasedate
        self.save_properties(title, description, sortorder, start_date, end_date, public_registration, allow_file, releasedate, lang)
            
        if REQUEST:
            self.setSessionInfo([MESSAGE_SAVEDCHANGES % self.utGetTodayDate()])
            REQUEST.RESPONSE.redirect('%s/edit_html?lang=%s' % (self.absolute_url(), lang))

    security.declareProtected(view, 'get_exfile')
    def get_exfile(self):
        """ Returns the first ExFile in the Simple Consultation, there should be only one. """
        
        try:
            exfile = self.objectValues(['Naaya Extended File'])[0]
        except IndexError:
            exfile = None
            
        return exfile

    security.declareProtected(view, 'check_exfile_for_lang')
    def check_exfile_for_lang(self, lang):
        """ Checks if there is a file uploaded for the given language. """
       
        return self.get_exfile().getFileItem(lang).size > 0

    security.declareProtected(view, 'get_exfile_langs')
    def get_exfile_langs(self):
        """ Returns the languages for witch NyExFile contains files. """
        
        return [language for language in self.getSite().gl_get_languages_map() if self.check_exfile_for_lang(language['id'])]

    security.declareProtected(view, 'get_start_date')
    def get_start_date(self):
        """ Returns the start date in dd/mm/yyyy string format. """
        
        return self.utConvertDateTimeObjToString(self.start_date)

    security.declareProtected(view, 'get_end_date')
    def get_end_date(self):
        """ Returns the end date in dd/mm/yyyy string format. """
        
        return self.utConvertDateTimeObjToString(self.end_date)
    
    security.declareProtected(view, 'get_days_left')
    def get_days_left(self):
        """ Returns the remaining days for the consultation or the number of days before it starts """
        
        today = self.utGetTodayDate().earliestTime()
        if not self.start_date or not self.end_date:
            return (1, 0)
        
        if self.start_date.lessThanEqualTo(today):
            return (1, int(str(self.end_date - today).split('.')[0]))
        else:
            return (0, int(str(self.start_date - today).split('.')[0]))

    security.declareProtected(view_management_screens, 'manage_options')
    def manage_options(self):
        """ """
        
        l_options = (NyContainer.manage_options[0],)
        l_options += ({'label': 'View', 'action': 'index_html'},) + NyContainer.manage_options[3:8]
        return l_options

    security.declareProtected(view, 'check_contributor_comment')
    def check_contributor_comment(self, contributor='', REQUEST=None):
        """ Returns True if user already posted a comment """
        
        if not contributor and REQUEST:
            contributor = REQUEST.AUTHENTICATED_USER.getUserName()
            
        return contributor in [comment.contributor for comment in self.objectValues(['Simple Consultation Comment'])]
        
    security.declareProtected(PERMISSION_REVIEW_SIMPLECONSULTATION, 'addComment')
    def addComment(self, title='', contributor_name='', message='', file='', REQUEST=None):
        """ """
        
        if not title or not contributor_name or not message:
            self.setSession('title', title)
            self.setSession('contributor_name', contributor_name)
            self.setSession('message', message)
            self.setSessionErrors(['Fill in all mandatory fields.'])
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_simpleconsultation_comment')
        
        contributor = REQUEST.AUTHENTICATED_USER.getUserName()
        if not self.allow_file: file = ''
        days = self.get_days_left()
        
        if days[0] == 1 and days[1] > 0:
            if not self.check_contributor_comment(contributor):
                addSimpleConsultationComment(self, title, contributor, contributor_name, message, file, REQUEST)
            else:
                return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_simpleconsultation_comment?status=failed')
        elif days[0] ==1 and days[1] <= 0:
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_simpleconsultation_comment?status=late')
        elif days[0] <= 0:
            return REQUEST.RESPONSE.redirect(self.absolute_url() + '/add_simpleconsultation_comment?status=soon')

    #permissions
    def checkPermissionReviewSimpleConsultation(self):
        """
        Check for reviewing the Simple Consultation.
        """
        return self.checkPermission(PERMISSION_REVIEW_SIMPLECONSULTATION)

    def checkPermissionManageSimpleConsultation(self):
        """
        Check for managing the Simple Consultation.
        """
        return self.checkPermission(PERMISSION_MANAGE_SIMPLECONSULTATION)

    #zmi pages
    security.declareProtected(view_management_screens, 'manage_edit_html')
    manage_edit_html = PageTemplateFile('zpt/simpleconsultation_manage_edit', globals())

    #site pages
    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/simpleconsultation_index', globals())
    
    security.declareProtected(PERMISSION_MANAGE_SIMPLECONSULTATION, 'edit_html')
    edit_html = PageTemplateFile('zpt/simpleconsultation_edit', globals())
    
    security.declareProtected(PERMISSION_REVIEW_SIMPLECONSULTATION, 'add_simpleconsultation_comment')
    add_simpleconsultation_comment = PageTemplateFile('zpt/simpleconsultation_comment_add', globals())

InitializeClass(NySimpleConsultation)
