#!/bin/bash

MARKUP_PREVIEW=$(dirname $(readlink -f ${BASH_SOURCE[0]}))
GEDIT_PLUGIN_DIR=~/.gnome2/gedit/plugins
LANGUAGE_SPEC_DIR=~/.local/share/gtksourceview-2.0/language-specs
MIME_DIR=~/.local/share/mime

echo "installing markup_preview plugin"
if [[ ! -d $GEDIT_PLUGIN_DIR ]]; then
    mkdir -p $GEDIT_PLUGIN_DIR
fi
cp -R $MARKUP_PREVIEW/plugin/* $GEDIT_PLUGIN_DIR

echo "installing markdown, rst, textile language-spec"
if [[ ! -d $LANGUAGE_SPEC_DIR ]]; then
    mkdir -p $LANGUAGE_SPEC_DIR
fi
cp -R $MARKUP_PREVIEW/language-spec/* $LANGUAGE_SPEC_DIR

echo "installing markdown MIME"
if [[ ! -d $MIME_DIR/packages ]]; then
    mkdir -p $MIME_DIR/packages
fi
cp -R $MARKUP_PREVIEW/mime/* $MIME_DIR/packages
update-mime-database $MIME_DIR
