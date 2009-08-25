from App.ImageFile import ImageFile

from Products.Naaya import register_content
import SemideRegistration
from utilities.StaticServe import StaticServeFromZip

ADD_PERMISSION = 'Add Semide Registration'

# Register as a folder content type
register_content(
    module=SemideRegistration,
    klass=SemideRegistration.SemideRegistration,
    module_methods={'manage_add_registration': ADD_PERMISSION, 'add_registration': ADD_PERMISSION},
    klass_methods={},
    add_method=('add_registration', ADD_PERMISSION),
)

def initialize(context):
    context.registerClass(
                          SemideRegistration.SemideRegistration,
                          permission = ADD_PERMISSION,
                          constructors=(
                                    SemideRegistration.add_registration,
                                    SemideRegistration.manage_add_registration),
                          icon='www/SemideRegistration.gif',
                          )

misc_ = {
    'tinymce': StaticServeFromZip('', 'www/tinymce_3_2_5.zip', globals()),
    'tinymceconfig.js': ImageFile('www/tinymceconfig.js', globals()),
    'calendar.js': ImageFile('www/calendar.js', globals()),
    'core.js': ImageFile('www/core.js', globals()),
    'datetime.js': ImageFile('www/datetime.js', globals()),
    'style.css': ImageFile('www/style.css', globals()),
    'SemideParticipant.png': ImageFile('www/SemideParticipant.png', globals()),
    'SemidePress.gif': ImageFile('www/SemidePress.gif', globals()),
    'print.gif': ImageFile('www/print.gif', globals()),
    }