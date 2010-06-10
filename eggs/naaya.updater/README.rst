Naaya updater
=============


Major code changes that require update scripts
----------------------------------------------
The listing starts from revision `14301`. Previous updates are not
covered.

r14484
    ExtJs removed in favour of jQuery. The `Update jQuery` script
    makes sure the correct version of jQuery is included.

r14557
    Big refactoring of ``GeoMapTool``. Run the update `Update properties
    of portal_map`. Also check that the `portal_map` default view looks
    right (it might have changed coordinates or zoom level).

r14640
    Schema widgets don't inherit from ``LocalPropertyManager`` anymore.
    The update script `Convert schema widget titles to string` will fix up
    their properties, otherwise widget labels (the ``title`` property)
    will not show correct values.
