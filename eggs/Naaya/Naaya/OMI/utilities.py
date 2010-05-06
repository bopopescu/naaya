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

import re
import string
import unicodedata
import types
from htmlentitydefs import name2codepoint
import random
import operator

from AccessControl import getSecurityManager

def generate_id():
    return str(random.randint(1000000,9999999))

def get_available_id(container, temp_container=None, id=None):
    if not id:
        id = generate_id()
    counter = 0
    while 1:
        buf = container._getOb(id, None)
        condition = buf
        if temp_container:
            buf_temp = temp_container._getOb(id, None)
            condition = buf_temp or buf
        if condition:
            prev_id = id
            if not counter:
                counter += 1
                id = '%s-%s' % (id, counter)
            else:
                id_pieces = prev_id.split('-')
                counter = int(id_pieces[-1]) + 1
                id = '%s-%s' % ('-'.join(id_pieces[:-1]), counter)
        else:
            break
    return id

def slugify(s, entities=True, decimal=True, hexadecimal=True, instance=None, slug_field='slug', filter_dict=None):
    s = smart_unicode(s)

    # character entity reference
    if entities:
        s = re.sub('&(%s);' % '|'.join(name2codepoint), lambda m: unichr(name2codepoint[m.group(1)]), s)

    # decimal character reference
    if decimal:
        try:
            s = re.sub('&#(\d+);', lambda m: unichr(int(m.group(1))), s)
        except:
            pass

    # hexadecimal character reference
    if hexadecimal:
        try:
            s = re.sub('&#x([\da-fA-F]+);', lambda m: unichr(int(m.group(1), 16)), s)
        except:
            pass

    # translate
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')

    # replace unwanted characters
    s = re.sub(r'[^-a-z0-9]+', '-', s.lower())

    # remove redundant -
    s = re.sub('-{2,}', '-', s).strip('-')

    return s

class Promise(object):
    """
    This is just a base class for the proxy class created in
    the closure of the lazy function. It can be used to recognize
    promises in code.
    """
    pass

def smart_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Returns a unicode object representing 's'. Treats bytestrings using the
    'encoding' codec.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if isinstance(s, Promise):
        # The input is the result of a gettext_lazy() call.
        return s
    return force_unicode(s, encoding, strings_only, errors)

def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_unicode, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.

    If strings_only is True, don't convert (some) non-string-like objects.
    """
    if strings_only and isinstance(s, (types.NoneType, int, long, datetime.datetime, datetime.date, datetime.time, float)):
        return s
    try:
        if not isinstance(s, basestring,):
            if hasattr(s, '__unicode__'):
                s = unicode(s)
            else:
                s = unicode(str(s), encoding, errors)
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
    except UnicodeDecodeError, e:
        # error log
        pass
    return s

def get_objects(catalogue, brains):
    for brain in brains:
        try:
            yield brain.getObject()
        except:
            pass # TODO: log this somewhere

def checkPermission(permission, object):
    """  Generic function to check a given permission on the current object. """
    return getSecurityManager().checkPermission(permission, object)

def sortObjsList(seq, attr, desc=1):
    """Sort a list of objects by an attribute values"""
    length = len(seq)
    temp = map(None, map(getattr, seq, (attr,)*length), xrange(length), seq)
    temp.sort()
    if desc:
        temp.reverse()
    return map(operator.getitem, temp, (-1,)*length)