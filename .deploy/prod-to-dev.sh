#!/bin/bash
#
# One-time copy all production data to your localhost
# You should be able to ssh to the db server and have rights to pg_dump proper schema

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

DB=$1

if [ -z $DB ]; then
    echo "Usage: ${0} <local_db_name>"
    exit 127
fi

start "Truncating local ${White}$DB${Green} database"
dropdb $DB
createdb $DB
finish

start "Copying prodution database"
ssh -C elk pg_dump -U dashboard --no-owner |psql -U elk -f - >/dev/null
finish
