import os.path

from zope.component import getAdapter
from zope.traversing.namespace import getResource
import zLOG

from contentratings.interfaces import IUserRating
from contentratings.browser.bbb import UserRatingSetView

from naaya.core.ggeocoding import GeocoderServiceError, reverse_geocode

class RatingOutOfBoundsError(Exception):
    def __init__(self, rating):
        self.rating = rating
    def __str__(self):
        return 'rating is %d' % self.rating

class ObservatoryRatingView(object):
    """A view for getting the rating information"""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = getAdapter(context, IUserRating,
                name=u'Observatory Rating')

        assert int(self.adapted.scale) == 5

    @property
    def rating(self):
        return int(round(self.adapted.averageRating))

    def __call__(self, REQUEST):
        if not (0 <= self.rating < 5):
            raise RatingOutOfBoundsError(self.rating)

        resource = getResource(self.context.getSite(),
                'naaya.observatory_rating_%d.icon' % self.rating, REQUEST)
        return resource.GET()

class ObservatoryRatingSetView(UserRatingSetView):
    """A view for setting the rating information"""

    #Overwriting this to have different keys for observatory ratings
    KEYBASE = 'observatory-anon-rated-'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.adapted = getAdapter(context, IUserRating,
                name=u'Observatory Rating')

        assert int(self.adapted.scale) == 5

    @property
    def address(self):
        address = self.context.geo_address()
        if address:
            return address

        if not self.context.geo_location:
            return ''
        if self.context.geo_location.missing_lat_lon:
            return ''

        lat = self.context.geo_latitude()
        lon = self.context.geo_longitude()
        try:
            return reverse_geocode(lat, lon)
        except GeocoderServiceError, e:
            zLOG.LOG('naaya.observatory', zLOG.PROBLEM, str(e))
            return ''


