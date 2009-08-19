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

import re
from OFS.Folder import Folder
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from DateTime import DateTime
from persistent.list import PersistentList
from Globals import Persistent
from operator import attrgetter


from utilities.Slugify import slugify
from Constants import *
import Participant


add_registration = PageTemplateFile('zpt/meeting_registration/add', globals())

def manage_add_registration(self, id='', title='', start_date='', end_date='', introduction='', REQUEST=None):
    """ Adds a meeting registration instance"""
    if registration_validation(mandatory_fields_registration, REQUEST, **REQUEST.form):
        if not id:
            id = slugify(title)
        ob = MeetingRegistration(id, title, start_date, end_date, introduction)
        self._setObject(id, ob)
        ob = self._getOb(id)
        if REQUEST:
            REQUEST.RESPONSE.redirect(self.absolute_url())
    else:
        return add_registration.__of__(self)(REQUEST)

email_expr = re.compile(r'^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$', re.IGNORECASE)

def registration_validation(mandatory_fields, REQUEST, **kwargs):
    """ Validates the new meeting registration fields """
    has_errors = False
    for k,v in kwargs.items():
        if k in mandatory_fields:
            if (k == 'email') and v:
                if not email_expr.match(v):
                    REQUEST.set('%s_notvalid' % k, True)
                    has_errors = True
            if k == (('start_date') or (k == 'end_date')) and v:
                try:
                    date = DateTime(v)
                except:
                    REQUEST.set('%s_invalid' % k, True)
                    has_errors = True
            if not v:
                REQUEST.set('%s_error' % k, True)
                has_errors = True
    if has_errors:
        REQUEST.set('request_error', True)
    return not has_errors

class MeetingRegistration(Folder):
    """ Main class of the meeting registration"""

    meta_type = 'Meeting registration'
    product_name = 'MeetingRegistration'

    security = ClassSecurityInfo()

    def __init__(self, id, title, start_date, end_date, introduction):
        """ constructor """
        self.id = id
        self.title = title
        self.start_date = start_date
        self.end_date = end_date
        self.introduction = introduction
        self.registration_form = PersistentList()
        self.registration_form_press = PersistentList()

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'addParticipant')
    addParticipant = Participant.addParticipant

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'index_html')
    index_html = PageTemplateFile('zpt/meeting_registration/index', globals())

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'edit')
    edit = PageTemplateFile('zpt/meeting_registration/edit', globals())

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'manage_edit_registration')
    def manage_edit_registration(self, id='', title='', start_date='', end_date='', introduction='', REQUEST=None):
        """ Edits the properties of the meeting registration """
        if registration_validation(mandatory_fields_registration, REQUEST, **REQUEST.form):
            self.title = title
            self.start_date = start_date
            self.end_date = end_date
            self.introduction = introduction
            if REQUEST:
                REQUEST.RESPONSE.redirect(self.absolute_url())
        else:
            return self.edit(REQUEST)

    security.declareProtected(EDIT_MEETING_REGISTRATION, '_form_edit')
    _form_edit = PageTemplateFile('zpt/registration_form/edit', globals())

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'form_edit')
    def form_edit(self, REQUEST):
        """ Edits the registration form, as it will be viewed by the participants"""
        edit_field_id = REQUEST.get('edit_field_id', '')
        if edit_field_id:
            field = self.registration_form[edit_field_id]
            REQUEST.set('field_id', field.id)
            REQUEST.set('field_type', field.field_type)
            REQUEST.set('field_label', field.field_label)
            REQUEST.set('field_content', field.field_content)
            REQUEST.set('mandatory', field.mandatory)
        return self._form_edit(REQUEST, field_types = field_types)

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'manage_addField')
    def manage_addField(self, REQUEST):
        """ Adds a new field to the registration form """
        from random import randrange
        
        if self.field_validation(mandatory_fields_field, REQUEST):
            request = REQUEST.form.get
            id = request('field_id', '')
            if not id:
                id = str(randrange(1000000,9999999))
            field_type = request('field_type')
            field_label = request('field_label')
            field_content = request('field_content', '')
            selection_values = request('selection_values', '')
            mandatory = request('mandatory', False)
            field_index = self.return_index(self.registration_form, id)
            if field_index is not None:
                self.registration_form[field_index] = FormField(id, field_type, field_label, field_content, selection_values, mandatory)
            else:
                self.registration_form.append(FormField(id, field_type, field_label, field_content, selection_values, mandatory))
            if REQUEST:
                REQUEST.RESPONSE.redirect(self.absolute_url()+'/form_edit')
                #return self.form_edit(None)
        else:
            return self.form_edit(REQUEST)

    def get_field_label(self, id):
        """ Returns the field label based on the field id """
        return self.registration_form[self.return_index(self.registration_form, id)].field_label

    def return_index(self, list, id):
        for field in list:
            if field.id == id:
                return list.index(field)
        return None

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'delete_field')
    def delete_field(self, id, REQUEST):
        """ deletes selected (id) field """
        del self.registration_form[self.return_index(self.registration_form, id)]
        #return REQUEST.RESPONSE.redirect(self.absolute_url()+'/form_edit')
        REQUEST.set('delete_field_id', '')
        REQUEST.set('field_deleted', True)
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/form_edit')

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'move_up_field')
    def move_up_field(self, id, REQUEST):
        """ Moves the selected field up in the display order """
        field_index  = self.return_index(self.registration_form, id)
        if field_index == 0:
            return
        temp_field = self.registration_form[field_index]
        self.registration_form[field_index] = self.registration_form[field_index - 1]
        self.registration_form[field_index - 1] = temp_field
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/form_edit')

    security.declareProtected(EDIT_MEETING_REGISTRATION, 'move_down_field')
    def move_down_field(self, id, REQUEST):
        """ Moves the selected field down in the display order """
        field_index = self.return_index(self.registration_form, id)
        if field_index == len(self.registration_form) - 1:
            return
        temp_field = self.registration_form[field_index]
        self.registration_form[field_index] = self.registration_form[field_index + 1]
        self.registration_form[field_index + 1] = temp_field
        return REQUEST.RESPONSE.redirect(self.absolute_url()+'/form_edit')

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'field_validation')
    def field_validation(self, mandatory_fields, REQUEST):
        """ Validates the field properties before adding a new field to the registration form """
        has_errors = False
        for field in mandatory_fields:
            if field not in REQUEST.form or not REQUEST.form.get(field):
                REQUEST.set('%s_error' % field, True)
                has_errors = True
            if REQUEST.form.get('field_type') == 'body_text' and not REQUEST.form.get('field_content'):
                REQUEST.set('body_text_error', True)
                has_errors = True
        if has_errors:
            REQUEST.set('request_error', True)
        return not has_errors

    security.declareProtected(ACCESS_MEETING_REGISTRATION, 'render_fields')
    def render_fields(self, is_editing = False):
        """ Renders the fields of the registration form """
        html_code = ''
        for field in self.registration_form:
            edit_link = self.absolute_url()+'/form_edit?edit_field_id='+field.id
            delete_link  = self.absolute_url()+'/form_edit?delete_field_id='+field.id
            move_up_link  = self.absolute_url()+'/move_up_field?id='+field.id
            move_down_link  = self.absolute_url()+'/move_down_field?id='+field.id
            if field.mandatory:
                label = '<td><label for="%s" i18n:translate="" style="color: #f40000">%s</label></td>' % (field.id, field.field_label)
            else:
                label = '<td><label for="%s" i18n:translate="">%s</label></td>' % (field.id, field.field_label)
            input_field = '<td><input id="%s" name="%s:utf8:ustring" type="text" size="50" /></td>' % (field.id, field.id)
            input_date = '''<td><input id="%s" name="%s" class="vDateField" type="text" size="10" maxlength="10" />
            <noscript><em class="tooltips">(dd/mm/yyyy)</em></noscript></td>''' % (field.id, field.id)
            input_checkbox = '<td><input id="%s" name="%s" type="checkbox" /></td>' % (field.id, field.id)
            input_selection_values = ''
            for value in field.selection_values:
                input_selection_values += '<input type="radio" name="%s" value="%s"/>%s<br/>' % (field.id, value, value)
            input_selection = '<td>' + input_selection_values + '</td>'
            textarea = '<td><textarea class="mceNoEditor" id="%s" name="%s:utf8:ustring" type="text" rows="5" cols="50" ></textarea></td>' % (field.id, field.id)
            body_text = '<td colspan="2">%s</td>' % field.field_content
            if is_editing:
                if len(self.registration_form) == 1:
                    buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td>' % (edit_link, delete_link)
                elif field == self.registration_form[0]:
                    buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td><td></td><td><span class="buttons"><a href="%s">Move down</a></span></td>' % (edit_link, delete_link, move_down_link)
                elif field == self.registration_form[-1]:
                    buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td><td><span class="buttons"><a href="%s">Move up</a></span></td></td><td>' % (edit_link, delete_link, move_up_link)
                else:
                    buttons = '<td><span class="buttons"><a href="%s">Edit</a></span></td><td><span class="buttons"><a href="%s">Delete</a></span></td><td><span class="buttons"><a href="%s">Move up</a></span></td><td><span class="buttons"><a href="%s">Move down</a></span></td>' % (edit_link, delete_link, move_up_link, move_down_link)
            else:
                buttons = ''

            if field.field_type == 'string_field':
                html_code = html_code + '<tr>' + label + input_field + buttons +'</tr>'
            if field.field_type == 'text_field':
                html_code = html_code + '<tr>' + label + textarea + buttons + '</tr>'
            if field.field_type == 'email_field':
                html_code = html_code + '<tr>' + label + input_field + buttons + '</tr>'
            if field.field_type == 'date_field':
                html_code = html_code + '<tr>' + label + input_date + buttons + '</tr>'
            if field.field_type == 'checkbox_field':
                html_code = html_code + '<tr>' + label + input_checkbox + buttons + '</tr>'
            if field.field_type == 'body_text':
                html_code = html_code + '<tr>' + body_text + buttons + '</tr>'
            if field.field_type == 'selection_field':
                html_code = html_code + '<tr>' + label + input_selection + buttons + '</tr>'
        return html_code

    new_registration = PageTemplateFile('zpt/registration_form/index', globals())

InitializeClass(MeetingRegistration)

class FormField(Persistent):
    ''' Defines the properties of a meeting registration field'''
    def __init__(self, id, field_type, field_label, field_content, selection_values, mandatory):
        self.id = id
        self.field_type = field_type
        self.field_label = field_label
        self.field_content = field_content
        self.mandatory = mandatory
        self.selection_values = selection_values

InitializeClass(FormField)