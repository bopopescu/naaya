from zope.interface import Interface

class INaayaPageTemplateFile(Interface):
    """ Marker interface """

class ITemplate(Interface):
    def __call__(*args, **kwargs):
        """Render the template"""

class ITemplateSource(Interface):
    """ Adapter interface used for getting the source of a template """

    def __call__():
        """ Return the source """
