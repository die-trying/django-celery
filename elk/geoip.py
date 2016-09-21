from os import path

import geoip2.database
from django.conf import settings


# TODO: unittest this class


class GeoIP():
    def __init__(self, ip):
        filename = path.join(settings.GEOIP_PATH, 'GeoLite2-City.mmdb')
        self.geoip = geoip2.database.Reader(filename)
        response = self.geoip.city(ip)

        self.country = response.country
        self.city = response.city
        self.location = response.location
