from os import path

import geoip2.database
from django.conf import settings
from timezonefinder import TimezoneFinder


class GeoIP():
    def __init__(self, ip):
        filename = path.join(settings.GEOIP_PATH, 'GeoLite2-City.mmdb')
        self.geoip = geoip2.database.Reader(filename)
        self._response = self.geoip.city(ip)

    @property
    def timezone(self):
        if self._response.location.time_zone is not None:
            return self._response.location.time_zone

        if self.lat is not None and self.lng is not None:
            tf = TimezoneFinder()
            return tf.timezone_at(
                lat=self.lat,
                lng=self.lng,
            )

    @property
    def country(self):
        return self._response.country.iso_code

    @property
    def city(self):
        return self._response.city.name

    @property
    def lat(self):
        return self._response.location.latitude

    @property
    def lng(self):
        return self._response.location.longitude
