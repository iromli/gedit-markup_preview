#!/bin/bash

MARKUP_PREVIEW=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
GEDIT_PLUGIN_DIR=~/.gnome2/gedit/plugins

echo "installing markup_preview plugin"
if [[ ! -d $GEDIT_PLUGIN_DIR ]]; then
    mkdir -p $GEDIT_PLUGIN_DIR
fi
cp -R $MARKUP_PREVIEW/plugin/* $GEDIT_PLUGIN_DIR
