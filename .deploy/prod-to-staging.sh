#!/bin/bash
#
# One-time copy all production data to the staging host
# to be run as root
#

set -e  # die on error

NC='\033[0m'              # Text Reset
Green='\033[0;32m'        # Green
Yellow='\033[0;33m'       # Yellow
Blue='\033[0;34m'         # Blue
White='\033[0;37m'        # White

function start {
    printf "${Green}${1}...${NC}\n"
}

function finish {
    printf " ${Yellow}Done.${NC}\n"
}

start "Truncating staging database"
sudo -u postgres dropdb staging
sudo -u postgres createdb staging
finish

start "Copying prodution database"
pg_dump -U dashboard --no-owner |psql -U staging -f - >/dev/null
finish

start "Updating media files"
rm -Rf /home/staging/media/*
cp -R /home/dashboard/media/* /home/staging/media/
finish
