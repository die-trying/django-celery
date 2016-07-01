#!/bin/sh

echo DROP DATABASE elk|mysql -uroot -p
echo CREATE DATABASE elk|mysql -uroot -p
./manage.py migrate