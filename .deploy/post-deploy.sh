#!/bin/bash

set -e	# die on error

function usage {
	printf "Usage: $0 <mode>\n"
	printf "Where <mode> can be 'staging' or 'production'\n"
}


if [ "$#" -eq 0 ]; then
	usage
	exit 127
fi;

if [ $1 != 'production' -a $1 != "staging" ]; then
	usage
	exit 127
fi;


MODE=$1
DIR='/home/dashboard'

NC='\033[0m'       		  # Text Reset
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

printf "${Blue}ELK dashboard post-deploy hook (${White}${MODE}${Blue})${NC}\n"

if [ "$1" = 'staging' ]; then
	DIR='/home/staging'
fi;

printf "${Green}Deployment root: ${White}${DIR}${NC}\n"
printf "\n\n\n"

cd $DIR

start "Activating venv"
. ./venv/bin/activate
printf " ${Yellow}Done - "
python --version

cd src

start "Installing requirements"
pip install --upgrade pip -q
pip install -r requirements.txt -q
finish

start "Restoring ${White}${MODE}${Green} configuration"
cp $DIR/.env.$MODE elk/.env
finish

start "Running migrations"
./manage.py migrate
finish

if [ "$MODE" = "production" ]; then
	start "Reloading background apps via supervirsorctl"
	sudo /usr/bin/supervisorctl restart celery
	sudo /usr/bin/supervisorctl restart celerybeat
	finish
fi;

start "Reloading main application"
touch $DIR/reload
finish

start "Updateing static files"
./manage.py collectstatic --noinput
finish
