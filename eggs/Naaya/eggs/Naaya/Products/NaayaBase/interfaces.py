from zope.interface import Interface, Attribute

from naaya.content.base.interfaces import INyContentObject

class INyContainer(Interface):
    """ Interface for NyContainer"""
    pass

class INyItem(Interface):
    """ Interface for NyItem"""
    pass

class INyFSFile(Interface):
    """ Interface for NyFSFile """
    pass


class INyAddLocalRoleEvent(Interface):
    """ Local role has been added """

    context = Attribute("Site or folder the roles are added for")
    name = Attribute("UID of the user the roles are added for")
    roles = Attribute("The list of roles")

class INySetLocalRoleEvent(Interface):
    """ Local role has been set """

    context = Attribute("Site or folder the roles are set for")
    name = Attribute("UID of the user the roles are set for")
    roles = Attribute("The list of roles")

class INyDelLocalRoleEvent(Interface):
    """ Local roles have been deleted """

    context = Attribute("Site or folder the roles are deleted for")
    names = Attribute("List of UIDs the roles are deleted for")


class INyAddUserRoleEvent(Interface):
    """ User  role has been added """

    context = Attribute("Site or folder the roles are added for")
    name = Attribute("UID of the user the roles are added for")
    roles = Attribute("The list of roles")

class INySetUserRoleEvent(Interface):
    """ User role has been set """

    context = Attribute("Site or folder the roles are set for")
    name = Attribute("UID of the user the roles are set for")
    roles = Attribute("The list of roles")

class INyDelUserRoleEvent(Interface):
    """ User roles have been deleted """

    context = Attribute("Site or folder the roles are deleted for")
    names = Attribute("List of UIDs the roles are deleted for")

