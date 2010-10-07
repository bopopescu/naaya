from datetime import datetime, timedelta
from urllib import quote
from oaipmh import server, metadata
from oaipmh.error import NoSetHierarchyError, BadResumptionTokenError

from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view_management_screens
from Acquisition import Implicit
from App.ImageFile import ImageFile
import DateTime
from Missing import Missing
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from zope import interface, schema

from ZCatalogHarvester import ZCatalogHarvester
from OAIRepository import OAIRepository
from OAIRecord import OAIRecord
from OAIToken import manage_addOAIToken

from interfaces import IOAIServer
from utils import create_object, process_form

#possible token keys
token_keys = ['metadataPrefix', 'offset', 'set', 'from', 'until']
def unserialize_token(token):
    "Split comma separated token and return a dictionary with values"
    token_dict = {}
    if isinstance(token, str):
        token_values  = token.split(',')
        for key in token_keys:
            try:
                token_dict[key] = token_values[token_keys.index(key)]
            except IndexError:
                token_dict[key] = ''
        return token_dict
    raise BadResumptionTokenError, 'unserialization failed'

def serialize_token(token):
    "Create a comma separated string for inclusion in the URL"
    if isinstance(token, dict):
        return ','.join([str(token.get(key, '')) for key in token_keys])
    raise BadResumptionTokenError, "dict expected"

manage_addOAIServerForm = PageTemplateFile('zpt/manage_addOAIServerForm',
                                           globals())
def manage_addOAIServer(self, id='', REQUEST=None, **kwargs):
    """ """
    if REQUEST is not None:
        form_data = dict(REQUEST.form)
    else:
        form_data = dict(kwargs)
    try:
        ob = create_object(self, OAIServer, id)
        process_form(ob, IOAIServer, form_data)
        ob.initialize()
    except Exception, e:
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=%s' % quote(str(e)))
        else:
            raise Exception(e)
    if REQUEST is not None:
        return REQUEST.RESPONSE.redirect(self.absolute_url() +
                                         '/manage_main?update_menu=1')

class OAIServer(OAIRepository):
    """ OAI2 Server implementation """
    interface.implements(IOAIServer)

    meta_type = 'OAI Server'
    all_meta_types = ({
        'name': ZCatalogHarvester.meta_type,
        'action':
            '/manage_addProduct/ZOpenArchives/manage_addZCatalogHarvesterForm',
        'product': ZCatalogHarvester.meta_type
        },
    )
    security = ClassSecurityInfo()

    stylesheet = ImageFile('www/celestial.xsl', globals())
    stylesheet.content_type = '	application/xml'

    def initialize(self):
        """ Create a oaipmh server to responde to OAI requests"""
        metadata_registry = metadata.MetadataRegistry()
        metadata_registry.registerWriter('oai_dc', server.oai_dc_writer)
        self.server = server.ServerBase(self, metadata_registry)
        self.base_url = self.absolute_url()
        super(OAIServer, self).initialize()

    security.declarePublic('index_html')
    def index_html(self, REQUEST=None, **kwargs):
        """ This is page that responds to the OAI2 requests. Uses PyOAI """
        if REQUEST is not None:
            response = self.server.handleRequest(REQUEST.form)
        else:
            response = self.server.handleRequest(kwargs)

        REQUEST.RESPONSE.setHeader('content-type', 'application/xml')
        #Add a stylesheet
        return response.replace("<?xml version='1.0' encoding='UTF-8'?>",
                         "<?xml version='1.0' encoding='UTF-8'?>\n"
                         "<?xml-stylesheet type='text/xsl'"
                         " href='" + self.absolute_url() + "/stylesheet'?>")

    security.declarePrivate('add_indexes')
    def add_indexes(self, catalog):
        """ Add indexes for catalog

        XXX:
        These indexes are not used currently because the OAI Record now
        contains 2 attributes: header and metadata.

        """
        # general searching - from web form
        catalog.addIndex('OAI_Date', 'FieldIndex')
        catalog.addIndex('OAI_Fulltext', 'TextIndexNG3')
        catalog.addIndex('OAI_Title', 'TextIndexNG3')

        # OAI Search stuff -
        catalog.addIndex('OAI_Identifier', 'FieldIndex')
        catalog.addIndex('OAI_Set', 'KeywordIndex')
        catalog.addIndex('status', 'FieldIndex')
        catalog.addIndex('OAI_MetadataFormat', 'FieldIndex')

        # dc search indexes
        catalog.addIndex('dc_title', 'TextIndexNG3')
        catalog.addIndex('dc_creator', 'KeywordIndex')
        catalog.addIndex('dc_author', 'KeywordIndex')
        catalog.addIndex('dc_subject', 'TextIndexNG3')
        catalog.addIndex('dc_description', 'TextIndexNG3')
        catalog.addIndex('dc_date', 'KeywordIndex')
        #Needed in ZCatalogHarvester
        catalog.addIndex('oai_state', 'FieldIndex')

        # lom search indexes
        # zope searching - in code
        catalog.addIndex('last_update', 'FieldIndex')
        try:
            catalog.addIndex('meta_type', 'FieldIndex')
        except:
            pass
        catalog.addIndex('expiration', 'FieldIndex')
        catalog.addIndex('path', 'PathIndex')

    def add_metadata(self, catalog):
        """ Adding metadata columns """
        #Add id and title columns if not present
        try:
            catalog.manage_addColumn('id')
        except:
            pass
        try:
            catalog.manage_addColumn('title')
        except:
            pass
        # ZOAI specific columns
        catalog.manage_addColumn('header')
        catalog.manage_addColumn('metadata')
        catalog.manage_addColumn('about')
        catalog.manage_addColumn('meta_type')

        catalog.manage_addColumn('OAI_Date')
        catalog.manage_addColumn('OAI_Title')
        catalog.manage_addColumn('OAI_Identifier')

        catalog.manage_addColumn('update_interval')
        catalog.manage_addColumn('last_update')

        catalog.manage_addColumn('dc_creator')
        catalog.manage_addColumn('dc_author')
        catalog.manage_addColumn('dc_description')
        catalog.manage_addColumn('dc_identifier')

    security.declarePrivate('update')
    def update(self, force=False):
        """ Update all harvesters """
        now = datetime.now()
        for item in self.objectValues([ZCatalogHarvester.meta_type]):
            if force or now > item.last_update + timedelta(
                                                days=item.update_interval):
                item.update()
        self.earliestDatestamp()
        super(OAIServer, self).update() #Update repository

    manage_preferences = PageTemplateFile("zpt/manage_OAIServerPrefsForm",
                                          globals())
    security.declareProtected(view_management_screens, 'manage_OAIServerPrefs')
    def manage_OAIServerPrefs(self, REQUEST=None, **kwargs):
        """ manage_preferences """
        if REQUEST is not None:
            form_data = dict(REQUEST.form)
        else:
            form_data = dict(kwargs)
        try:
            process_form(self, IOAIServer, form_data)
        except Exception, e:
            if REQUEST is not None:
                return REQUEST.RESPONSE.redirect(self.absolute_url() +
                    '/manage_main?manage_tabs_message=%s' % quote(str(e)))
            else:
                raise Exception(e)
        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_preferences?manage_tabs_message=Settings%20saved')

    security.declareProtected(view_management_screens, 'manage_update')
    def manage_update(self, REQUEST=None):
        """ Manually update all harvesters """
        self.update(True)

        if REQUEST is not None:
            return REQUEST.RESPONSE.redirect(self.absolute_url() +
                '/manage_main?manage_tabs_message=Harvesters%20updated')

    ################
    # Protocol
    ################

    security.declarePrivate('baseURL')
    def baseURL(self):
        return self.base_url

    security.declarePrivate('repositoryName')
    def repositoryName(self):
        """ """
        return self.repository_name

    security.declarePrivate('protocolVersion')
    def protocolVersion(self):
        """ """
        return self.protocol_version

    security.declarePrivate('adminEmails')
    def adminEmails(self):
        return [x.strip() for x in self.admin_emails.split(',') if x.strip()]

    security.declarePrivate('earliestDatestamp')
    def earliestDatestamp(self):
        """ Last OAIRecord in the repository """
        if getattr(self, 'earliest_datestamp', None):
            return self.earliest_datestamp
        else:
            results = self.getCatalog().searchResults({
                'meta_type': OAIRecord.meta_type,
                'sort_on':'OAI_Date',
                'sort_order':'reverse'
            })
            if len(results) == 0:
                date = datetime.now()
            else:
                date = results[0].OAI_Date
            self.earliest_datestamp = date
            return date

    security.declarePrivate('granularity')
    def granularity(self):
        """ """
        return self.date_granularity

    def get_date(self, date_str=None):
        """ Return fixed date string depending on granularity of server """
        if date_str == None:
            date = DateTime.DateTime()
        else:
            date = DateTime.DateTime(date_str)
        granularity = self.granularity()
        if granularity == 'YYYY-MM-DD':
            d_str = str(date.strftime("%Y-%m-%d"))
        elif granularity == 'YYYY-MM-DDThh:mm:ssZ':
            d_str = str(date.HTML4())
        else:
            raise "Unknown granularity: '%s'", granularity
        return d_str

    security.declarePrivate('deletedRecord')
    def deletedRecord(self):
        """ """
        return self.deleted_record

    security.declarePrivate('compression')
    def compression(self):
        """ Not implemented """
        return []

    security.declarePrivate('descriptions')
    def descriptions(self):
        """ Not implemented """
        return []

    security.declarePrivate('identify')
    def identify(self):
        """ Used in pyoai """
        return self

    security.declarePrivate('listIdentifiers')
    def listIdentifiers(self, **kw):
        """ """
        raise NotImplementedError

    security.declarePrivate('listMetadataFormats')
    def listMetadataFormats(self, **kw):
        """ Metadata formats from namespace dictionary
        TODO: Fix this when the indexes in the ZCatalog are set right.

        """
        metadata_formats = []
        if kw.has_key('identifier'):
            search_dict = {
                'meta_type': OAIRecord.meta_type,
                'OAI_Identifier': kw['identifier']
            }
            if len(results) == 0:
                raise ValueError("OAI Error: idDoesNotExist")
            results = self.getCatalog().searchResults(search_dict)
            for record in results:
                ns_prefix = record.metadata_format
                metadata_formats.append(self.get_namespace_dict(ns_prefix))
            if len(the_list) == 0:
                raise ValueError("OAI Error: noMetadataFormats")
        else:
            data_dict = self.get_namespace_dict('oai_dc')
            metadata_formats.append((data_dict['prefix'], data_dict['schema'],
                                     data_dict['namespace']))
        return metadata_formats

    security.declarePrivate('listSets')
    def listSets(self, **kw):
        """ Not supported """
        raise NoSetHierarchyError

    security.declarePrivate('listRecords')
    def listRecords(self, **kw):
        token = None
        offset = 0
        search_dict = {'meta_type': OAIRecord.meta_type}
        search_dict['sort_limit'] = self.results_limit
        """Get the args for the request either from our 'resumption token' or
        from our regular request dictionary"""
        if kw.has_key('resumptionToken'):
            #Unserialize the token and populate search_dict
            token = unserialize_token(kw['resumptionToken'])
            offset = int(token.get('offset', 0))
        results = self.getCatalog().searchResults(search_dict)

        record_count = 0
        len_results = len(results)
        results_list = [] #Return list
        resumptionToken = ''
        while (offset + record_count) < len_results:
            # get search record and info
            record = results[offset+record_count]
            header = getattr(record, 'header', "")
            metadata = getattr(record, 'metadata', "")
            about = getattr(record, 'about', "")
            record_count += 1
            if (isinstance(header, Missing) or isinstance(metadata, Missing) or
                isinstance(about, Missing)):
                continue

            results_list.append([header, metadata, about])

            #Create a Token if limit is reached
            if record_count >= self.results_limit:
                new_token = {}
                new_token['offset'] = offset + record_count
                if token is None:
                    for key, value in kw.items():
                        if key in token_keys:
                            new_token[key] = value
                    resumptionToken = serialize_token(new_token)
                else:
                    token['offset'] = new_token['offset']
                    resumptionToken = serialize_token(token)

                #Not supported in pyoai
                #token_args = {}
                #token_args['cursor'] = offset
                #token_args['completeListSize'] = len_results
                #token_args['expirationDate'] = (DateTime.DateTime() +
                #                    (self.token_expiration/1440.0)).HTML4()
                #token_args['resumptionToken'] = resumptionToken

                break
        return (results_list, resumptionToken)
