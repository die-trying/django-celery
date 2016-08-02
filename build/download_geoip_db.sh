#!/bin/sh
cd geolite
wget -c http://geolite.maxmind.com/download/geoip/database/GeoLiteCity.dat.gz
wget -c http://geolite.maxmind.com/download/geoip/database/GeoLiteCityv6-beta/GeoLiteCityv6.dat.gz

gunzip -kqf GeoLiteCity.dat.gz
gunzip -kqf GeoLiteCityv6.dat.gz