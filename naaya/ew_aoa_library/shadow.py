from OFS.SimpleItem import SimpleItem
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import view, view_management_screens

from naaya.core.utils import path_in_site

def extract_checkboxmatrix(answer, widget_name):
    widget = answer.getSurveyTemplate()[widget_name]
    datamodel = answer.get(widget_name)
    if datamodel is None:
        return []

    out = []
    for index, row_answers in enumerate(datamodel):
        for answer in row_answers:
            out.append( (widget.rows[index], widget.choices[answer]) )

    return out

def extract_multipleselect(answer, widget_name):
    widget = answer.getSurveyTemplate()[widget_name]
    datamodel = answer.get(widget_name)
    if datamodel is None:
        return []
    else:
        return [widget.choices[n] for n in datamodel]

geo_type_map = {
    ('Global',   'Green Economy'):  'symbol634',
    ('Global',   'Water'):          'symbol634',
    ('Regional', 'Green Economy'):  'symbol997',
    ('Regional', 'Water'):          'symbol997',
    ('National', 'Green Economy'):  'symbol767',
    ('National', 'Water'):          'symbol767',
}

def extract_geo_type(answer):
    for key in extract_checkboxmatrix(answer, 'w_theme'):
        if key in geo_type_map:
            return geo_type_map[key]
    else:
        return None

widgetidmap = {
    'theme': 'w_theme',
    'geo_location': 'w_theme1115',
    'water_resorces': 'w_2-if-water-specify-which-following-topics-are',
    'water_resource_management': 'w_water-resource-management-specify-which-he',
    'green_economy': 'w_if-green-economy-specify-which-following-topics',
    'resource_efficiency': 'w_resource-efficiency-specify-which-following',

    'assessment_location': 'w_source-ie-location-assessment',
    'assessment_name': 'w_name-assessment',
    'body_conducting_assessment': 'w_name-body-conducting-assessment',
    'year': 'w_year-which-assessment-has-been-published',
    'url': 'w_url',
    'uploaded_file': 'w_if-not-available-please-upload-assessment',
    'specific_scope': 'w_assembled-selected-knowledge-ie-specify-if',
    'formal': 'w_formal-ie-specify-if-assessment-has-defined-scope',
    'publically_available': 'w_publicly-available-ie-specify-if-assessment',
    'other_criteria': 'w_are-there-other-criteria-basis-which-you-would',
    'priority_main_criterion': 'w_if-yes-specify-main-criterion',
    'name': 'w_name',
    'email': 'w_email',
    'organisation': 'w_organisation',
}

public_widgets = set(widgetidmap[x] for x in (
    'theme',
    'geo_location',
    'water_resorces',
    'water_resource_management',
    'green_economy',
    'resource_efficiency',

    'assessment_location',
    'assessment_name',
    'body_conducting_assessment',
    'year',
    'url',
    'uploaded_file',
    'specific_scope',
    'formal',
    'publically_available',
    'other_criteria',
    'priority_main_criterion',
))

def extract_survey_answer_data(answer):
    attrs = {
        'id': answer.getId(),
        'title': answer.get('w_name-assessment'),
        'geo_location': answer.get('w_theme1115'),
        'uploader': answer.get('w_15-information-about-data-uploader'),
        'geo_type': extract_geo_type(answer),
        'description': "",
        'target_path': path_in_site(answer),
    }

    if not attrs['title']:
        answer_id = attrs['id']
        prefix = 'answer_'
        if answer_id.startswith(prefix):
            answer_id = answer_id[len(prefix):]
        attrs['title'] = "Assessment %s" % answer_id

    return attrs

class AssessmentShadow(SimpleItem):
    """ Non-persistent shadow object that describes an AoA assessment """

    manage_options = (
        {'label': 'Summary', 'action': 'manage_main'},
        {'label': 'View', 'action': ''},
    ) + SimpleItem.manage_options[1:]

    meta_type = "Naaya EW_AOA Shadow Object"

    submitted = 1
    approved = 1

    security = ClassSecurityInfo()

    def __init__(self, id, **attrs):
        self._setId(id)
        self.__dict__.update(attrs)

    def geo_latitude(self):
        if self.geo_location is None:
            raise AttributeError
        if self.geo_location.lat is None:
            raise AttributeError
        return self.geo_location.lat

    def geo_longitude(self):
        if self.geo_location is None:
            raise AttributeError
        if self.geo_location.lon is None:
            raise AttributeError
        return self.geo_location.lon

    security.declareProtected(view_management_screens, 'target_answer')
    def target_answer(self):
        return self.getSite().restrictedTraverse(self.target_path)

    security.declareProtected(view, 'render_answer')
    def render_answer(self):
        answer = self.target_answer()
        datamodel = answer.getDatamodel()
        survey_template = answer.getSurveyTemplate()

        views = []
        for widget in survey_template.getSortedWidgets():
            if widget.id not in public_widgets:
                continue
            widget_data = datamodel.get(widget.id)
            views.append(widget.render(mode='view', datamodel=widget_data))

        return '\n'.join(views)

    security.declareProtected(view, 'index_html')
    index_html = PageTemplateFile('zpt/assessment_index', globals())

    manage_main = PageTemplateFile('zpt/assessment_manage_main', globals())

def shadow_for_answer(answer):
    attrs = extract_survey_answer_data(answer)
    return AssessmentShadow(**attrs)

#print "loaded survey data module"
