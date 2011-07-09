#!/bin/bash

# SCRIPT_DIR
cd `dirname $0`

echo "installing Markup Preview plugin for Gedit"
PLUGIN_DIR=~/.gnome2/gedit/plugins
if [[ ! -d $PLUGIN_DIR ]]; then
    mkdir -p $PLUGIN_DIR
fi
cp -R plugin/* $PLUGIN_DIR

echo "installing markup MIME files for Gedit"
MIME_DIR=~/.local/share/mime
if [[ ! -d $MIME_DIR/packages ]]; then
    mkdir -p $MIME_DIR/packages
fi
cp -R mime/* $MIME_DIR/packages
update-mime-database $MIME_DIR
