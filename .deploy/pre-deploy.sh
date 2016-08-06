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

printf "${Blue}ELK dashboard pre-deploy hook (${White}${MODE}${Blue})${NC}\n"

if [ "$1" = 'staging' ]; then
	DIR='/home/staging'
fi;

printf "${Green}Deployment root: ${White}${DIR}${NC}\n"
printf "\n\n"

cd $DIR

start "Preserving configuration files"
cp src/elk/.env .env.$MODE.preserved
finish
