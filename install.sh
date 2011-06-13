#!/bin/bash

# SCRIPT_DIR
cd `dirname $0`
echo "installing Markup Preview plugin for Gedit"
cp -R markup_preview/* ~/.gnome2/gedit/plugins
