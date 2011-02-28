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
# Alex Morega, Eau de Web
# David Batranu, Eau de Web

import urllib

from ZODB.blob import Blob
from Persistence import Persistent
from ZPublisher.Iterators import filestream_iterator

from naaya.core.utils import mimetype_from_filename

COPY_BLOCK_SIZE = 65536 # 64KB
DEFAULT_MIMETYPE = 'application/octet-stream'

class NyBlobFile(Persistent):
    """
    Naaya container for files stored using ZODB Blob
    """

    def __init__(self, **kwargs):
        kwargs.setdefault('filename', None)
        kwargs.setdefault('content_type', 'application/octet-stream')
        for key, value in kwargs.iteritems():
            setattr(self, key, value)
        self._blob = Blob()

    def open(self):
        return self._blob.open('r')

    def open_iterator(self):
        return filestream_iterator(self._blob.committed(), 'rb')

    def open_write(self):
        return self._blob.open('w')

    def send_data(self, RESPONSE, as_attachment=True, set_filename=True,
                  REQUEST=None):
        """NyBlobFiles can also be served using X-Sendfile.
        In order to do so, you need to set X-NaayaEnableSendfile header
        to "on" by frontend server for each request.

        Lighttpd.conf example (working in proxy mode)::
         server.modules  += ( "mod_setenv" )
         setenv.add-request-header = ( "X-NaayaEnableSendfile" => "on" )
         proxy-core.allow-x-sendfile = "enable"

        """
        RESPONSE.setHeader('Content-Length', self.size)
        RESPONSE.setHeader('Content-Type', self.content_type)
        if as_attachment:
            header_value = "attachment"
            if set_filename:
                utf8_fname = urllib.quote(self.filename)
                header_value += ";filename*=UTF-8''%s" % utf8_fname
            RESPONSE.setHeader('Content-Disposition', header_value)

        # Test for enabling of X-SendFile
        if REQUEST is not None:
            ny_xsendfile = REQUEST.get_header("X-NaayaEnableSendfile")
            if ny_xsendfile is not None and ny_xsendfile=="on":
                RESPONSE.setHeader("X-Sendfile",
                                   self._blob._current_filename())
                return "[body should be replaced by front-end server]"

        if hasattr(RESPONSE, '_streaming'):
            return self.open_iterator()
        else:
            return self.open().read()

    def __repr__(self):
        return '<%(cls)s %(fname)r (%(mime)s, %(size)r bytes)>' % {
            'cls': self.__class__.__name__,
            'fname': self.filename,
            'mime': self.content_type,
            'size': self.size,
        }

def make_blobfile(the_file, **kwargs):
    filename = trim_filename(the_file.filename)

    content_type = getattr(the_file, 'headers', {}).get('content-type', None)
    if content_type is None:
        content_type = mimetype_from_filename(filename, DEFAULT_MIMETYPE)

    meta = {
        'filename': filename,
        'content_type': content_type,
    }
    meta.update(kwargs)

    blobfile = NyBlobFile(**meta)

    # copy file data
    bf_stream = blobfile.open_write()
    size = 0
    while True:
        data = the_file.read(COPY_BLOCK_SIZE)
        if not data:
            break
        bf_stream.write(data)
        size += len(data)
    bf_stream.close()
    blobfile.size = size

    return blobfile

def trim_filename(filename):
    """
    Internet Explorer sends us the complete file path, not just the
    file's name, so we need to strip that.
    """
    return filename.rsplit('\\', 1)[-1]
