import warnings
from naaya.content import file as newlocation

warnings.warn(
    '%s is deprecated. Use %s instead'  % (__name__, newlocation.__name__),
    DeprecationWarning, stacklevel=2)
