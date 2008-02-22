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
# Agency (EEA).  Portions created by Finsiel Romania and Eau de Web are
# Copyright (C) European Environment Agency.  All
# Rights Reserved.
#
# Authors:
#
# Cristian Ciupitu, Eau de Web

# Zope imports
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from BaseMultipleChoiceStatistics import BaseMultipleChoiceStatistics
import pygooglechart

class MultipleChoiceCssBarChartStatistics(BaseMultipleChoiceStatistics):
    """Barchart ...
    """

    security = ClassSecurityInfo()

    _constructors = (lambda *args, **kw: manage_addStatistic(MultipleChoiceCssBarChartStatistics, *args, **kw), )

    meta_type = "Naaya Survey - Multiple Choice CSS Bar Chart Statistics"
    meta_label = "Multiple Choice CSS Bar Chart Statistics"
    meta_description = """Bar chart for every choice"""
    meta_sortorder = 211
    icon_filename = 'statistics/www/multiplechoice_css_barchart_statistics.gif'

    security.declarePublic('render')
    def render(self, answers):
        """Render statistics as HTML code"""
        total, answered, unanswered, per_choice = self.calculate(self.question, answers)
        return self.page(question=self.question,
                         total=total,
                         answered=answered,
                         unanswered=unanswered,
                         per_choice=per_choice)

    page = PageTemplateFile("zpt/multiplechoice_css_barchart_statistics.zpt", globals())

InitializeClass(MultipleChoiceCssBarChartStatistics)

def getStatistic():
    return MultipleChoiceCssBarChartStatistics
