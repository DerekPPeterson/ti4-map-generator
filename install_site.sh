#!/usr/bin/env bash

INSTALL_SITE_PATH=/var/www/html/

cmake ./
make 
rsync ti4-map-generator site/cgi-bin
rsync -avzP site/ $INSTALL_SITE_PATH
mkdir -p $INSTALL_SITE_PATH/generated
chown -R www-data $INSTALL_SITE_PATH/generated
