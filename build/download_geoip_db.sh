#!/bin/sh
#
# Downloads maxmind database from http://dev.maxmind.com/geoip/legacy/geolite/
#

cd geolite

wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
wget -N http://geolite.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz

gunzip -kqf GeoIP.dat.gz
gunzip -kqf GeoLiteCity.dat.gz
