#!/bin/sh
#
# Downloads maxmind database from http://dev.maxmind.com/geoip/legacy/geolite/
#

cd geolite

wget -N http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz

gunzip -kqf GeoLite2-City.mmdb.gz
