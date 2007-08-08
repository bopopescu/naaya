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
# Agency (EEA). Portions created by Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Alec Ghica, Eau de Web
# Cornel Nitu, Eau de Web

from ImageFile import ImageFile
import NaayaUpdater

UpdaterID = NaayaUpdater.UPDATERID

from NaayaPatches import *

def initialize(context):
    """ """

    #add Naaya Updater
    app = context._ProductContext__app
    global updater

    if hasattr(app, UpdaterID):
        updater = getattr(app, UpdaterID)
    else:
        try:
            updater = NaayaUpdater.NaayaUpdater(id=UpdaterID)
            app._setObject(UpdaterID, updater)
            get_transaction().note('Added Naaya Updater')
            get_transaction().commit()
        except:
            pass
        updater = getattr(app, UpdaterID)
    assert updater is not None


misc_ = {
    "updater.jpg":  ImageFile("www/updater.jpg", globals()),
}