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
# Agency (EEA).  Portions created by Finsiel Romania are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alex Morega, Eau de Web
# Cornel Nitu, Eau de Web
# Valentin Dumitru, Eau de Web

from App.ImageFile import ImageFile

from Products.Naaya import register_content
import MeetingRegistration
from utilities.StaticServe import StaticServeFromZip

ADD_PERMISSION = 'Add Meeting Registration'

# Register as a folder content type
register_content(
    module=MeetingRegistration,
    klass=MeetingRegistration.MeetingRegistration,
    module_methods={'manage_add_registration': ADD_PERMISSION, 'add_registration': ADD_PERMISSION},
    klass_methods={},
    add_method=('add_registration', ADD_PERMISSION),
)


def initialize(context):
    context.registerClass(
                          MeetingRegistration.MeetingRegistration,
                          permission = ADD_PERMISSION,
                          constructors=(
                                    MeetingRegistration.add_registration,
                                    MeetingRegistration.manage_add_registration),
                          icon='www/MeetingRegistration.gif',
                          )

misc_ = {
    'tinymce': StaticServeFromZip('', 'www/tinymce_3_2_5.zip', globals()),
}