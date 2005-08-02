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
# Cornel Nitu, Finsiel Romania
# Dragos Chirila, Finsiel Romania

#Python imports
from os import listdir
from os.path import join, isdir
import time
from copy import copy

#Zope imports
from ImageFile import ImageFile

#Product imports
from constants import *

#read list of directories
dirs = []
for x in listdir(NAAYACONTENT_PRODUCT_PATH):
    if isdir(join(NAAYACONTENT_PRODUCT_PATH, x)) and x.startswith('Ny'):
        dirs.append(x)

#run imports
content = {}
err_list = []
for x in dirs:
    #try:
    c = 'from %s import %s' % (x, x)
    exec(c)
    m = eval('%s.METATYPE_OBJECT' % x)
    content[m] = {}
    content[m]['product'] = NAAYACONTENT_PRODUCT_NAME
    content[m]['module'] = x
    content[m]['meta_type'] = m
    content[m]['label'] = eval('%s.LABEL_OBJECT' % x)
    content[m]['permission'] = eval('%s.PERMISSION_ADD_OBJECT' % x)
    content[m]['forms'] = copy(eval('%s.OBJECT_FORMS' % x))
    content[m]['constructors'] = copy(eval('%s.OBJECT_CONSTRUCTORS' % x))
    content[m]['addform'] = eval('%s.OBJECT_ADD_FORM' % x)
    content[m]['validation'] = eval('%s.TOBE_VALIDATED' % x)
    content[m]['description'] = eval('%s.DESCRIPTION_OBJECT' % x)
    #print '%s INFO Successfully loaded pluggable module %s.' % (time.ctime(), x)
    #except Exception, error:
    #    err_list.append(x)
    #    print '%s ERROR loading pluggable module %s: %s' % (time.ctime(), x, str(error))

#clean up
for x in err_list:
    dirs.remove(x)

def get_pluggable_content():
    return content

def initialize(context):
    """ """

    #register classes
    for x in content.values():
        m, p, a = x['module'], x['permission'], x['addform']
        c = """context.registerClass(
            %s.%s,
            permission='%s',
            constructors=(%s.manage_add%s_html, %s.add%s, %s.%s),
            icon='%s/www/%s.gif',
            visibility=None
        )""" % (m, m, p, m, m, m, m, m, a, m, m)
        exec(c)

misc_ = {
}

#images
for x in dirs:
    misc_['%s.gif' % x] = ImageFile('%s/www/%s.gif' % (x, x), globals())
    misc_['%s_marked.gif' % x] = ImageFile('%s/www/%s_marked.gif' % (x, x), globals())
