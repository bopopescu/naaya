def handler_approved(event):
    """ After an object is approved update flash tool """

    ob = event.context
    portal = ob.getSite()

    flashtool_ob = portal.getFlashTool()
    if flashtool_ob:
        flashtool_ob.addfornotif_object(ob)

def handler_unapproved(event):
    """ After an object is approved update flash tool """

    ob = event.context
    portal = ob.getSite()

    flashtool_ob = portal.getFlashTool()
    if flashtool_ob:
        flashtool_ob.delfornotif_object(ob)
